"""Чтение Source-engine .vpk (v1 / v2) и виртуальная "библиотека звуков"
для SoundScapeEditor. Только stdlib."""
import atexit
import hashlib
import os
import re
import shutil
import struct
import tempfile
import time

VPK_SIGNATURE = 0x55AA1234
ARCHIVE_IN_DIR = 0x7FFF           # данные лежат в самом _dir.vpk, после дерева
AUDIO_EXTS = (".wav", ".mp3", ".ogg")
TMP_PREFIX = "ssevpk-"          # ssevpk-<pid>-xxxx  (текущий формат временной папки)
LEGACY_TMP_PREFIX = "sse_vpk_"  # старый формат без pid


class VPKError(Exception):
    pass


class VPKDuplicate(VPKError):
    """VPK уже подключён: тот же файл, его часть (_000, _001...) или точная копия."""
    def __init__(self, existing, reason="same"):
        super().__init__("already mounted: " + existing.path)
        self.existing = existing
        self.reason = reason


class VPKArchive:
    """Один VPK-набор (xxx_dir.vpk + xxx_000.vpk, xxx_001.vpk ... или одиночный .vpk)."""

    @staticmethod
    def resolve_path(path):
        """Абсолютный путь; если выбрали часть xxx_000.vpk — заменяет на xxx_dir.vpk рядом."""
        path = os.path.abspath(path)
        m = re.match(r"^(.*)_(\d{3})\.vpk$", path, re.I)
        if m:
            for suffix in ("_dir.vpk", "_Dir.vpk", "_DIR.vpk"):
                if os.path.isfile(m.group(1) + suffix):
                    return m.group(1) + suffix
        return path

    def __init__(self, path):
        self.path = self.resolve_path(path)
        self.signature = ""
        self.entries = {}            # "sound/a/b.wav" (lower) -> (real_path, crc, preload, arch, off, len)
        self._data_offset = 0
        self._sound_count = None
        self._parse()

    # ---------- разбор ----------
    def _parse(self):
        try:
            f = open(self.path, "rb")
        except OSError as e:
            raise VPKError(str(e))
        with f:
            head = f.read(12)
            if len(head) < 12:
                raise VPKError("файл слишком короткий")
            sig, ver, tree_size = struct.unpack("<III", head)
            if sig != VPK_SIGNATURE:
                if re.search(r"_\d{3}\.vpk$", self.path, re.I):
                    raise VPKError("это часть многофайлового VPK, выберите файл *_dir.vpk")
                raise VPKError("это не VPK (неверная сигнатура)")
            if ver == 1:
                header_size = 12
            elif ver == 2:
                header_size = 28
            else:
                raise VPKError(f"неподдерживаемая версия VPK: {ver}")
            f.seek(header_size)
            tree = f.read(tree_size)
        if len(tree) < tree_size:
            raise VPKError("дерево VPK повреждено")
        self._data_offset = header_size + tree_size
        # отпечаток содержимого: одинаковое дерево (пути, CRC, смещения) = тот же VPK
        self.signature = hashlib.md5(head + tree).hexdigest()
        self._parse_tree(tree)

    def _parse_tree(self, t):
        pos = 0
        n = len(t)

        def cstr():
            nonlocal pos
            end = t.index(b"\0", pos)
            s = t[pos:end].decode("utf-8", "replace")
            pos = end + 1
            return s

        try:
            while pos < n:
                ext = cstr()
                if ext == "":
                    break
                while True:
                    d = cstr()
                    if d == "":
                        break
                    while True:
                        name = cstr()
                        if name == "":
                            break
                        crc, pre_len, arch, off, length, term = struct.unpack_from("<IHHIIH", t, pos)
                        pos += 18
                        if term != 0xFFFF:
                            raise VPKError("битая запись в дереве")
                        preload = t[pos:pos + pre_len]
                        pos += pre_len
                        e = "" if ext == " " else ext
                        dd = "" if d == " " else d
                        full = (dd + "/" if dd else "") + name + ("." + e if e else "")
                        self.entries[full.lower()] = (full, preload, arch, off, length)
        except (ValueError, struct.error):
            raise VPKError("дерево VPK повреждено")

    # ---------- чтение ----------
    def _archive_path(self, idx):
        if idx == ARCHIVE_IN_DIR:
            return self.path
        base = self.path[:-8] if self.path.lower().endswith("_dir.vpk") else self.path[:-4]
        return "%s_%03d.vpk" % (base, idx)

    def has(self, key):
        return key.lower() in self.entries

    def read(self, key):
        full, preload, arch, off, length = self.entries[key.lower()]
        data = preload
        if length:
            fp = self._archive_path(arch)
            if arch == ARCHIVE_IN_DIR:
                off += self._data_offset
            with open(fp, "rb") as f:
                f.seek(off)
                data += f.read(length)
        return data

    def sound_count(self):
        if self._sound_count is None:
            self._sound_count = sum(
                1 for k in self.entries if k.startswith("sound/") and k.endswith(AUDIO_EXTS))
        return self._sound_count

    def sound_files(self):
        """Пути внутри sound/, БЕЗ префикса 'sound/' (как в wave = "..." в soundscape)."""
        out = []
        for low, (full, *_rest) in self.entries.items():
            if low.startswith("sound/") and low.endswith(AUDIO_EXTS):
                out.append(full[6:])
        return out


def _pid_alive(pid):
    """Жив ли процесс с таким pid. При любых сомнениях считаем, что жив."""
    if pid <= 0:
        return False
    try:
        if os.name == "nt":
            import ctypes
            k = ctypes.windll.kernel32
            k.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
            k.OpenProcess.restype = ctypes.c_void_p
            k.GetExitCodeProcess.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
            k.CloseHandle.argtypes = [ctypes.c_void_p]
            h = k.OpenProcess(0x1000, 0, pid)        # PROCESS_QUERY_LIMITED_INFORMATION
            if not h:
                return ctypes.GetLastError() == 5    # ACCESS_DENIED: процесс есть
            try:
                code = ctypes.c_ulong()
                if k.GetExitCodeProcess(h, ctypes.byref(code)):
                    return code.value == 259         # STILL_ACTIVE
                return True
            finally:
                k.CloseHandle(h)
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            return True
        return True
    except Exception:
        return True


def _only_audio(path):
    """True, если внутри папки лежат только звуковые файлы (наша временная папка)."""
    for _dp, _dn, files in os.walk(path):
        for f in files:
            if not f.lower().endswith(AUDIO_EXTS):
                return False
    return True


class SoundLibrary:
    """Набор подключённых VPK. Умеет искать звук и распаковывать его во временный файл
    (QMediaPlayer играет только с диска). Временные файлы удаляются:
      * при отключении VPK (только файлы этого VPK),
      * при выходе из программы (atexit / cleanup()),
      * при следующем запуске (sweep_stale) — если программа завершилась аварийно."""

    def __init__(self):
        self.vpks = []
        self._tmp = None
        self._pending = []      # папки, которые не удалось стереть (файл занят плеером)
        atexit.register(self.cleanup)

    # ---------- временные папки ----------
    def _session_dir(self):
        if self._tmp is None or not os.path.isdir(self._tmp):
            self._tmp = tempfile.mkdtemp(prefix="%s%d-" % (TMP_PREFIX, os.getpid()))
        return self._tmp

    def _vpk_dir(self, vpk_path):
        tag = hashlib.md5(os.path.normcase(vpk_path).encode("utf-8")).hexdigest()[:10]
        return os.path.join(self._tmp, tag)

    def _remove_dir(self, d):
        """Удаляет папку. Если что-то занято — запоминает и пробует позже (flush_pending)."""
        if os.path.isdir(d):
            shutil.rmtree(d, ignore_errors=True)
        if os.path.isdir(d):
            if d not in self._pending:
                self._pending.append(d)
            return False
        if d in self._pending:
            self._pending.remove(d)
        return True

    def flush_pending(self):
        for d in list(self._pending):
            self._remove_dir(d)

    # ---------- подключение ----------
    @staticmethod
    def _same_file(a, b):
        if os.path.normcase(os.path.abspath(a)) == os.path.normcase(os.path.abspath(b)):
            return True
        try:
            return os.path.samefile(a, b)      # ссылки, короткие имена, другой регистр
        except OSError:
            return False

    def mount(self, path):
        """Подключает VPK. Бросает VPKDuplicate, если он (или его часть / копия) уже подключён,
        и VPKError, если файл не читается."""
        path = VPKArchive.resolve_path(path)   # xxx_000.vpk -> xxx_dir.vpk
        for v in self.vpks:
            if self._same_file(v.path, path):
                raise VPKDuplicate(v, "same")
        v = VPKArchive(path)                    # бросит VPKError при проблемах
        for m in self.vpks:
            if m.signature and m.signature == v.signature:
                raise VPKDuplicate(m, "copy")   # тот же VPK, лежащий в другой папке
        self.vpks.append(v)
        return v

    def unmount(self, path):
        """Отключает VPK и удаляет распакованные из него звуки."""
        path = os.path.normcase(os.path.abspath(path))
        self.vpks = [v for v in self.vpks if os.path.normcase(v.path) != path]
        if self._tmp:
            self._remove_dir(self._vpk_dir(path))

    def clear(self):
        old = self.vpks
        self.vpks = []
        if self._tmp:
            for v in old:
                self._remove_dir(self._vpk_dir(v.path))

    def paths(self):
        return [v.path for v in self.vpks]

    @staticmethod
    def _norm(rel):
        rel = str(rel).strip().replace("\\", "/").lstrip("/")
        if rel.lower().startswith("sound/"):
            rel = rel[6:]
        return rel

    def find(self, rel):
        key = "sound/" + self._norm(rel)
        for v in self.vpks:
            if v.has(key):
                return v, key
        return None

    def extract(self, rel):
        """Локальный путь к распакованному звуку или None."""
        hit = self.find(rel)
        if not hit:
            return None
        v, key = hit
        self._session_dir()
        d = self._vpk_dir(v.path)
        tag = hashlib.md5((v.path + "|" + key).encode("utf-8")).hexdigest()[:12]
        out = os.path.join(d, tag + os.path.splitext(key)[1])
        if not os.path.isfile(out):
            try:
                os.makedirs(d, exist_ok=True)
                data = v.read(key)
                with open(out, "wb") as f:
                    f.write(data)
            except OSError:
                return None
        return out

    def all_sounds(self):
        """[(rel_path, имя_vpk), ...]"""
        res = []
        for v in self.vpks:
            label = os.path.basename(v.path)
            res.extend((p, label) for p in v.sound_files())
        return res

    # ---------- уборка ----------
    def cleanup(self):
        """Удаляет всю временную папку этой сессии (вызывается при выходе)."""
        if self._tmp:
            shutil.rmtree(self._tmp, ignore_errors=True)
            if not os.path.isdir(self._tmp):
                self._tmp = None
        self._pending = []

    @staticmethod
    def sweep_stale(legacy_min_age=120):
        """Удаляет временные папки, оставшиеся от прошлых запусков (сбой, kill, чужой pid мёртв).
        Трогает только папки с нашим префиксом, в которых лежат одни звуки."""
        base = tempfile.gettempdir()
        try:
            names = os.listdir(base)
        except OSError:
            return 0
        removed = 0
        now = time.time()
        for n in names:
            p = os.path.join(base, n)
            if os.path.islink(p) or not os.path.isdir(p):
                continue
            m = re.match(r"^" + re.escape(TMP_PREFIX) + r"(\d+)-", n)
            if m:
                pid = int(m.group(1))
                if pid == os.getpid() or _pid_alive(pid):
                    continue
            elif n.startswith(LEGACY_TMP_PREFIX):
                try:
                    if now - os.path.getmtime(p) < legacy_min_age:
                        continue
                except OSError:
                    continue
            else:
                continue
            if not _only_audio(p):
                continue
            shutil.rmtree(p, ignore_errors=True)
            if not os.path.isdir(p):
                removed += 1
        return removed