import hashlib
import hmac
import json
import os
import platform
import re
import subprocess
import tempfile
import time
import uuid
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

class MachineIDError(Exception):

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "MACHINE_ID_ERROR"
        self.context = context or {}
        self.timestamp = time.time()

    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message='{self.message}', error_code='{self.error_code}')"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "context": self.context,
            "timestamp": self.timestamp,
        }

class MachineIDNotFound(MachineIDError):

    def __init__(
        self,
        message: str = "无法获取机器标识符",
        platform: Optional[str] = None,
        attempted_methods: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ):

        error_context = context or {}
        if platform:
            error_context["platform"] = platform
        if attempted_methods:
            error_context["attempted_methods"] = attempted_methods

        super().__init__(message, "MACHINE_ID_NOT_FOUND", error_context)
        self.platform = platform
        self.attempted_methods = attempted_methods or []

    def add_attempted_method(self, method: str) -> None:
        if method not in self.attempted_methods:
            self.attempted_methods.append(method)
            self.context["attempted_methods"] = self.attempted_methods

class PlatformNotSupported(MachineIDError):

    def __init__(
        self,
        message: str = "当前平台不受支持",
        platform: Optional[str] = None,
        supported_platforms: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ):

        error_context = context or {}
        if platform:
            error_context["current_platform"] = platform
        if supported_platforms:
            error_context["supported_platforms"] = supported_platforms

        super().__init__(message, "PLATFORM_NOT_SUPPORTED", error_context)
        self.platform = platform
        self.supported_platforms = supported_platforms or [
            "Windows",
            "Linux",
            "macOS",
            "BSD",
        ]

    def get_suggestion(self) -> str:
        if self.supported_platforms:
            platforms_str = ", ".join(self.supported_platforms)
            return f"请在以下支持的平台上运行: {platforms_str}"
        return "请检查平台兼容性"

class HardwareInfoError(MachineIDError):

    def __init__(
        self,
        message: str = "无法获取硬件信息",
        hardware_type: Optional[str] = None,
        command: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):

        error_context = context or {}
        if hardware_type:
            error_context["hardware_type"] = hardware_type
        if command:
            error_context["failed_command"] = command

        super().__init__(message, "HARDWARE_INFO_ERROR", error_context)
        self.hardware_type = hardware_type
        self.command = command

class CacheError(MachineIDError):
    def __init__(
        self,
        message: str = "缓存操作失败",
        operation: Optional[str] = None,
        cache_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):

        error_context = context or {}
        if operation:
            error_context["operation"] = operation
        if cache_type:
            error_context["cache_type"] = cache_type

        super().__init__(message, "CACHE_ERROR", error_context)
        self.operation = operation
        self.cache_type = cache_type

def protect_id(app_id: str, machine_id: str) -> str:
    mac = hmac.new(machine_id.encode("utf-8"), app_id.encode("utf-8"), hashlib.sha256)
    return mac.hexdigest()

def format_id(machine_id: str, format_type: str = "raw") -> str:
    if format_type == "raw":
        return sanitize_id(machine_id)
    elif format_type == "uuid":
        return format_as_uuid(machine_id)
    elif format_type == "md5":
        return hashlib.md5(machine_id.encode("utf-8")).hexdigest()
    elif format_type == "sha256":
        return hashlib.sha256(machine_id.encode("utf-8")).hexdigest()
    else:
        raise ValueError(f"不支持的格式类型: {format_type}")

def sanitize_id(machine_id: str) -> str:
    cleaned = re.sub(r"[\x00-\x1f\x7f-\x9f\s]", "", machine_id)
    return cleaned.strip().upper()

def format_as_uuid(machine_id: str) -> str:
    if is_valid_uuid(machine_id):
        return machine_id.upper()

    hash_obj = hashlib.md5(machine_id.encode("utf-8"))
    hex_str = hash_obj.hexdigest()

    return f"{hex_str[:8]}-{hex_str[8:12]}-{hex_str[12:16]}-{hex_str[16:20]}-{hex_str[20:32]}".upper()

def is_valid_uuid(test_string: str) -> bool:
    try:
        uuid.UUID(test_string)
        return True
    except ValueError:
        return False

def validate_machine_id(machine_id: str) -> bool:
    if not machine_id or len(machine_id.strip()) == 0:
        return False

    cleaned = sanitize_id(machine_id)
    if len(cleaned) < 8:
        return False

    invalid_patterns = ["unknown", "default", "none", "null", "0000", "ffff"]
    cleaned_lower = cleaned.lower()

    for pattern in invalid_patterns:
        if pattern in cleaned_lower:
            return False

    return True

class CacheManager:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
        self.ttl = self.config.get("ttl", 3600)
        self.file_cache_enabled = self.config.get("file_cache", False)
        self.cache_dir = self.config.get("cache_dir") or tempfile.gettempdir()
        self.max_entries = self.config.get("max_entries", 100)

        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_file = os.path.join(self.cache_dir, "machine_id_cache.json")

        if self.file_cache_enabled:
            self._load_file_cache()

    def get(self, key: str) -> Optional[str]:
        if not self.enabled:
            return None

        value = self._get_from_memory(key)
        if value is not None:
            return value

        if self.file_cache_enabled:
            value = self._get_from_file(key)
            if value is not None:
                self._set_to_memory(key, value)
                return value

        return None

    def set(self, key: str, value: str) -> None:
        if not self.enabled:
            return

        try:
            self._set_to_memory(key, value)

            if self.file_cache_enabled:
                self._set_to_file(key, value)

        except Exception:
            pass

    def delete(self, key: str) -> None:
        if not self.enabled:
            return

        if key in self._memory_cache:
            del self._memory_cache[key]

        if self.file_cache_enabled:
            self._delete_from_file(key)

    def clear(self) -> None:
        if not self.enabled:
            return

        self._memory_cache.clear()

        if self.file_cache_enabled:
            try:
                if os.path.exists(self._cache_file):
                    os.remove(self._cache_file)
            except OSError:
                pass

    def cleanup_expired(self) -> None:
        if not self.enabled:
            return

        current_time = time.time()
        expired_keys = []

        for key, cache_item in self._memory_cache.items():
            if current_time - cache_item["timestamp"] > self.ttl:
                expired_keys.append(key)

        for key in expired_keys:
            del self._memory_cache[key]

        if self.file_cache_enabled:
            self._cleanup_file_cache()

    def get_stats(self) -> Dict[str, Any]:
        stats = {
            "enabled": self.enabled,
            "memory_entries": len(self._memory_cache),
            "ttl": self.ttl,
            "file_cache_enabled": self.file_cache_enabled,
            "max_entries": self.max_entries,
        }

        if self.file_cache_enabled:
            stats["cache_file"] = self._cache_file
            stats["cache_file_exists"] = os.path.exists(self._cache_file)

            if stats["cache_file_exists"]:
                try:
                    stats["cache_file_size"] = os.path.getsize(self._cache_file)
                except OSError:
                    stats["cache_file_size"] = -1

        return stats

    def _get_from_memory(self, key: str) -> Optional[str]:
        if key not in self._memory_cache:
            return None

        cache_item = self._memory_cache[key]
        current_time = time.time()

        if current_time - cache_item["timestamp"] > self.ttl:
            del self._memory_cache[key]
            return None

        return cache_item["value"]

    def _set_to_memory(self, key: str, value: str) -> None:
        if len(self._memory_cache) >= self.max_entries:
            oldest_key = min(
                self._memory_cache.keys(),
                key=lambda k: self._memory_cache[k]["timestamp"],
            )
            del self._memory_cache[oldest_key]

        self._memory_cache[key] = {"value": value, "timestamp": time.time()}

    def _get_from_file(self, key: str) -> Optional[str]:
        try:
            if not os.path.exists(self._cache_file):
                return None

            with open(self._cache_file, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            if key not in cache_data:
                return None

            cache_item = cache_data[key]
            current_time = time.time()

            if current_time - cache_item["timestamp"] > self.ttl:
                return None

            return cache_item["value"]

        except (IOError, json.JSONDecodeError, KeyError):
            return None

    def _set_to_file(self, key: str, value: str) -> None:
        try:
            os.makedirs(self.cache_dir, exist_ok=True)

            cache_data = {}
            if os.path.exists(self._cache_file):
                try:
                    with open(self._cache_file, "r", encoding="utf-8") as f:
                        cache_data = json.load(f)
                except (json.JSONDecodeError, IOError):
                    cache_data = {}

            cache_data[key] = {"value": value, "timestamp": time.time()}

            with open(self._cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=2)

        except (IOError, OSError):
            pass

    def _delete_from_file(self, key: str) -> None:
        try:
            if not os.path.exists(self._cache_file):
                return

            with open(self._cache_file, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            if key in cache_data:
                del cache_data[key]

                with open(self._cache_file, "w", encoding="utf-8") as f:
                    json.dump(cache_data, f, indent=2)

        except (IOError, json.JSONDecodeError):
            pass

    def _load_file_cache(self) -> None:
        try:
            if not os.path.exists(self._cache_file):
                return

            with open(self._cache_file, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            current_time = time.time()

            for key, cache_item in cache_data.items():
                if current_time - cache_item["timestamp"] <= self.ttl:
                    if len(self._memory_cache) < self.max_entries:
                        self._memory_cache[key] = cache_item

        except (IOError, json.JSONDecodeError):
            pass

    def _cleanup_file_cache(self) -> None:
        try:
            if not os.path.exists(self._cache_file):
                return

            with open(self._cache_file, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            current_time = time.time()
            cleaned_data = {}

            for key, cache_item in cache_data.items():
                if current_time - cache_item["timestamp"] <= self.ttl:
                    cleaned_data[key] = cache_item

            if len(cleaned_data) != len(cache_data):
                with open(self._cache_file, "w", encoding="utf-8") as f:
                    json.dump(cleaned_data, f, indent=2)

        except (IOError, json.JSONDecodeError):
            pass

class BasePlatformAdapter(ABC):
    def __init__(self):
        self.system_info = self._get_system_info()

    @abstractmethod
    def get_system_id(self) -> str:
        raise NotImplementedError("子类必须实现 get_system_id 方法")

    def get_hardware_id(self) -> str:
        hardware_info = self._collect_hardware_info()
        combined_info = "|".join(
            [
                hardware_info.get("motherboard_serial", "unknown"),
                hardware_info.get("cpu_id", "unknown"),
                hardware_info.get("mac_address", "unknown"),
                hardware_info.get("disk_serial", "unknown"),
                self.system_info.get("system", "unknown"),
                self.system_info.get("machine", "unknown"),
            ]
        )

        return hashlib.sha256(combined_info.encode("utf-8")).hexdigest()

    def get_hybrid_id(self) -> str:
        try:
            system_id = self.get_system_id()
            if validate_machine_id(system_id):
                return system_id
        except Exception:
            pass

        return self.get_hardware_id()

    def _collect_hardware_info(self) -> Dict[str, str]:
        info = {}

        try:
            info["motherboard_serial"] = self._get_motherboard_serial()
        except Exception:
            info["motherboard_serial"] = "unknown"

        try:
            info["cpu_id"] = self._get_cpu_id()
        except Exception:
            info["cpu_id"] = "unknown"

        try:
            info["mac_address"] = self._get_mac_address()
        except Exception:
            info["mac_address"] = "unknown"

        try:
            info["disk_serial"] = self._get_disk_serial()
        except Exception:
            info["disk_serial"] = "unknown"

        return info

    def _get_system_info(self) -> Dict[str, str]:
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        }

    def _get_mac_address(self) -> str:
        mac = uuid.getnode()
        return ":".join(
            ["{:02x}".format((mac >> ele) & 0xFF) for ele in range(0, 8 * 6, 8)][::-1]
        )

    @abstractmethod
    def _get_motherboard_serial(self) -> str:
        raise NotImplementedError("子类必须实现 _get_motherboard_serial 方法")

    @abstractmethod
    def _get_cpu_id(self) -> str:
        raise NotImplementedError("子类必须实现 _get_cpu_id 方法")

    def _get_disk_serial(self) -> str:
        return "unknown"

    def _execute_command(self, command: str, shell: bool = True) -> Optional[str]:
        try:
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=10,
                check=True,
            )
            return result.stdout.strip()
        except (subprocess.SubprocessError, subprocess.TimeoutExpired):
            return None

    def _read_file(self, filepath: str) -> Optional[str]:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read().strip()
        except (IOError, OSError):
            return None

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "platform": self.system_info.get("system", "unknown"),
            "supports_system_id": True,
            "supports_hardware_id": True,
            "supports_hybrid_id": True,
            "hardware_sources": [
                "motherboard_serial",
                "cpu_id",
                "mac_address",
                "disk_serial",
            ],
        }

class WindowsPlatformAdapter(BasePlatformAdapter):
    def get_system_id(self) -> str:
        machine_id = self._get_machine_guid_from_registry()
        if machine_id:
            return sanitize_id(machine_id)

        machine_id = self._get_machine_guid_from_powershell()
        if machine_id:
            return sanitize_id(machine_id)

        machine_id = self._get_machine_guid_from_wmic()
        if machine_id:
            return sanitize_id(machine_id)

        raise MachineIDNotFound("无法获取Windows MachineGuid")

    def _get_machine_guid_from_registry(self) -> Optional[str]:
        try:
            import winreg

            key_path = r"SOFTWARE\Microsoft\Cryptography"

            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                machine_guid, _ = winreg.QueryValueEx(key, "MachineGuid")
                return machine_guid

        except ImportError:
            return None
        except (OSError, FileNotFoundError):
            return None

    def _get_machine_guid_from_powershell(self) -> Optional[str]:
        command = 'powershell.exe -ExecutionPolicy bypass -command "(Get-CimInstance -Class Win32_ComputerSystemProduct).UUID"'
        result = self._execute_command(command)

        if result and result.lower() not in ["", "null", "none"]:
            return result
        return None

    def _get_machine_guid_from_wmic(self) -> Optional[str]:
        command = "wmic csproduct get uuid"
        result = self._execute_command(command)

        if result:
            lines = result.split("\n")
            for line in lines:
                line = line.strip()
                if line and line.lower() not in ["uuid", "", "null", "none"]:
                    return line
        return None

    def _get_motherboard_serial(self) -> str:
        command = "wmic baseboard get serialnumber"
        result = self._execute_command(command)

        if result:
            lines = result.split("\n")
            for line in lines:
                line = line.strip()
                if line and line.lower() not in ["serialnumber", "", "null", "none"]:
                    return line

        command = 'powershell.exe -command "(Get-CimInstance -Class Win32_BaseBoard).SerialNumber"'
        result = self._execute_command(command)

        if result and result.lower() not in ["", "null", "none"]:
            return result

        return "unknown"

    def _get_cpu_id(self) -> str:
        command = "wmic cpu get processorid"
        result = self._execute_command(command)

        if result:
            lines = result.split("\n")
            for line in lines:
                line = line.strip()
                if line and line.lower() not in ["processorid", "", "null", "none"]:
                    return line

        command = 'powershell.exe -command "(Get-CimInstance -Class Win32_Processor).ProcessorId"'
        result = self._execute_command(command)

        if result and result.lower() not in ["", "null", "none"]:
            return result

        command = "wmic cpu get name"
        result = self._execute_command(command)

        if result:
            lines = result.split("\n")
            for line in lines:
                line = line.strip()
                if line and line.lower() not in ["name", "", "null", "none"]:
                    return line

        return self.system_info.get("processor", "unknown")

    def _get_disk_serial(self) -> str:
        command = 'wmic logicaldisk where caption="C:" get volumeserialnumber'
        result = self._execute_command(command)

        if result:
            lines = result.split("\n")
            for line in lines:
                line = line.strip()
                if line and line.lower() not in [
                    "volumeserialnumber",
                    "",
                    "null",
                    "none",
                ]:
                    return line

        return "unknown"

class LinuxPlatformAdapter(BasePlatformAdapter):
    MACHINE_ID_PATHS = ["/var/lib/dbus/machine-id", "/etc/machine-id"]

    def get_system_id(self) -> str:
        for path in self.MACHINE_ID_PATHS:
            machine_id = self._read_file(path)
            if machine_id and len(machine_id.strip()) > 0:
                return sanitize_id(machine_id)

        container_id = self._get_container_id()
        if container_id:
            return sanitize_id(container_id)

        wsl_id = self._get_wsl_id()
        if wsl_id:
            return sanitize_id(wsl_id)

        raise MachineIDNotFound("无法获取Linux machine-id")

    def _get_container_id(self) -> Optional[str]:
        docker_id = self._get_docker_id()
        if docker_id:
            return docker_id

        return None

    def _get_docker_id(self) -> Optional[str]:
        cgroup_content = self._read_file("/proc/self/cgroup")
        if cgroup_content and "docker" in cgroup_content:
            command = "head -1 /proc/self/cgroup | cut -d/ -f3"
            result = self._execute_command(command)
            if result and len(result) >= 12:
                return result

        mountinfo_content = self._read_file("/proc/self/mountinfo")
        if mountinfo_content and "docker" in mountinfo_content:
            command = "grep -oP '(?<=docker/containers/)([a-f0-9]+)(?=/hostname)' /proc/self/mountinfo"
            result = self._execute_command(command)
            if result:
                return result

        return None

    def _get_wsl_id(self) -> Optional[str]:
        if "microsoft" in self.system_info.get("release", "").lower():
            command = "powershell.exe -ExecutionPolicy bypass -command '(Get-CimInstance -Class Win32_ComputerSystemProduct).UUID'"
            result = self._execute_command(command)
            if result and result.lower() not in ["", "null", "none"]:
                return result

        return None

    def _get_motherboard_serial(self) -> str:
        dmi_serial = self._read_file("/sys/class/dmi/id/board_serial")
        if dmi_serial and dmi_serial.lower() not in [
            "",
            "null",
            "none",
            "not specified",
        ]:
            return dmi_serial

        command = "dmidecode -s baseboard-serial-number"
        result = self._execute_command(command)
        if result and result.lower() not in ["", "null", "none", "not specified"]:
            return result

        alternative_paths = [
            "/sys/class/dmi/id/product_serial",
            "/sys/class/dmi/id/chassis_serial",
        ]

        for path in alternative_paths:
            serial = self._read_file(path)
            if serial and serial.lower() not in ["", "null", "none", "not specified"]:
                return serial

        return "unknown"

    def _get_cpu_id(self) -> str:
        cpuinfo = self._read_file("/proc/cpuinfo")
        if cpuinfo:
            for line in cpuinfo.split("\n"):
                line = line.strip()
                if line.startswith("processor") and ":" in line:
                    continue
                if any(
                    key in line.lower()
                    for key in ["serial", "processor id", "cpu serial"]
                ):
                    if ":" in line:
                        value = line.split(":", 1)[1].strip()
                        if value and value.lower() not in ["", "null", "none"]:
                            return value

        command = "dmidecode -t processor | grep 'ID:'"
        result = self._execute_command(command)
        if result:
            lines = result.split("\n")
            for line in lines:
                if "ID:" in line:
                    cpu_id = line.split("ID:", 1)[1].strip()
                    if cpu_id and cpu_id.lower() not in ["", "null", "none"]:
                        return cpu_id

        if cpuinfo:
            for line in cpuinfo.split("\n"):
                if line.startswith("model name") and ":" in line:
                    model = line.split(":", 1)[1].strip()
                    if model:
                        return model
                    break

        return self.system_info.get("processor", "unknown")

    def _get_disk_serial(self) -> str:
        command = (
            "lsblk -no SERIAL $(df / | tail -1 | awk '{print $1}' | sed 's/[0-9]*$//')"
        )
        result = self._execute_command(command)
        if result and result.lower() not in ["", "null", "none"]:
            return result

        command = "udevadm info --query=property --name=$(df / | tail -1 | awk '{print $1}' | sed 's/[0-9]*$//') | grep ID_SERIAL_SHORT"
        result = self._execute_command(command)
        if result and "=" in result:
            serial = result.split("=", 1)[1].strip()
            if serial and serial.lower() not in ["", "null", "none"]:
                return serial

        try:
            for device in os.listdir("/sys/block"):
                if device.startswith(("sd", "nvme", "hd")):
                    serial_path = f"/sys/block/{device}/device/serial"
                    serial = self._read_file(serial_path)
                    if serial and serial.lower() not in ["", "null", "none"]:
                        return serial
        except (OSError, IOError):
            pass

        return "unknown"

class DarwinPlatformAdapter(BasePlatformAdapter):
    def get_system_id(self) -> str:
        platform_uuid = self._get_platform_uuid_from_ioreg()
        if platform_uuid:
            return sanitize_id(platform_uuid)

        platform_uuid = self._get_platform_uuid_from_system_profiler()
        if platform_uuid:
            return sanitize_id(platform_uuid)

        raise MachineIDNotFound("无法获取macOS IOPlatformUUID")

    def _get_platform_uuid_from_ioreg(self) -> Optional[str]:
        command = "ioreg -rd1 -c IOPlatformExpertDevice"
        result = self._execute_command(command)

        if result:
            return self._extract_platform_uuid(result)

        return None

    def _get_platform_uuid_from_system_profiler(self) -> Optional[str]:
        command = "system_profiler SPHardwareDataType"
        result = self._execute_command(command)

        if result:
            for line in result.split("\n"):
                line = line.strip()
                if "Hardware UUID:" in line or "Platform UUID:" in line:
                    uuid_match = re.search(
                        r"([A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12})",
                        line,
                        re.IGNORECASE,
                    )
                    if uuid_match:
                        return uuid_match.group(1)

        return None

    def _extract_platform_uuid(self, ioreg_output: str) -> Optional[str]:
        for line in ioreg_output.split("\n"):
            if "IOPlatformUUID" in line:
                uuid_match = re.search(
                    r'"([A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12})"',
                    line,
                    re.IGNORECASE,
                )
                if uuid_match:
                    return uuid_match.group(1)

                if "=" in line:
                    parts = line.split("=", 1)
                    if len(parts) == 2:
                        uuid_candidate = parts[1].strip().strip('"')
                        if re.match(
                            r"^[A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12}$",
                            uuid_candidate,
                            re.IGNORECASE,
                        ):
                            return uuid_candidate

        return None

    def _get_motherboard_serial(self) -> str:
        command = "system_profiler SPHardwareDataType"
        result = self._execute_command(command)

        if result:
            for line in result.split("\n"):
                line = line.strip()
                if "Serial Number:" in line:
                    serial = line.split("Serial Number:", 1)[1].strip()
                    if serial and serial.lower() not in ["", "null", "none"]:
                        return serial

        command = "ioreg -l | grep IOPlatformSerialNumber"
        result = self._execute_command(command)

        if result:
            serial_match = re.search(r'"([^"]+)"', result)
            if serial_match:
                serial = serial_match.group(1)
                if serial and serial.lower() not in ["", "null", "none"]:
                    return serial

        return "unknown"

    def _get_cpu_id(self) -> str:
        command = "system_profiler SPHardwareDataType"
        result = self._execute_command(command)

        if result:
            cpu_info = []
            for line in result.split("\n"):
                line = line.strip()
                if any(
                    key in line
                    for key in [
                        "Processor Name:",
                        "Processor Speed:",
                        "Number of Processors:",
                    ]
                ):
                    cpu_info.append(line)

            if cpu_info:
                return " | ".join(cpu_info)

        command = "sysctl -n machdep.cpu.brand_string"
        result = self._execute_command(command)
        if result:
            return result

        command = "sysctl -n hw.model"
        result = self._execute_command(command)
        if result:
            return result

        return self.system_info.get("processor", "unknown")

    def _get_disk_serial(self) -> str:
        command = "diskutil info / | grep 'Device / Media Name'"
        result = self._execute_command(command)
        if result:
            return result.split(":", 1)[1].strip() if ":" in result else result

        command = "system_profiler SPStorageDataType"
        result = self._execute_command(command)

        if result:
            for line in result.split("\n"):
                line = line.strip()
                if "Serial Number:" in line:
                    serial = line.split("Serial Number:", 1)[1].strip()
                    if serial and serial.lower() not in ["", "null", "none"]:
                        return serial

        command = "ioreg -r -c IOBlockStorageDriver"
        result = self._execute_command(command)

        if result:
            serial_match = re.search(r'"Device Serial Number" = "([^"]+)"', result)
            if serial_match:
                serial = serial_match.group(1)
                if serial and serial.lower() not in ["", "null", "none"]:
                    return serial

        return "unknown"

class BSDPlatformAdapter(BasePlatformAdapter):
    def get_system_id(self) -> str:
        hostid = self._read_file("/etc/hostid")
        if hostid and len(hostid.strip()) > 0:
            return sanitize_id(hostid)

        smbios_uuid = self._get_smbios_uuid()
        if smbios_uuid:
            return sanitize_id(smbios_uuid)

        sysctl_id = self._get_sysctl_machine_id()
        if sysctl_id:
            return sanitize_id(sysctl_id)

        raise MachineIDNotFound("无法获取BSD系统ID")

    def _get_smbios_uuid(self) -> Optional[str]:
        command = "kenv -q smbios.system.uuid"
        result = self._execute_command(command)

        if result and result.lower() not in ["", "null", "none"]:
            return result

        return None

    def _get_sysctl_machine_id(self) -> Optional[str]:
        sysctl_keys = ["kern.hostuuid", "hw.uuid", "machdep.dmi.system-uuid"]

        for key in sysctl_keys:
            command = f"sysctl -n {key}"
            result = self._execute_command(command)
            if result and result.lower() not in ["", "null", "none"]:
                return result

        return None

    def _get_motherboard_serial(self) -> str:
        command = "dmidecode -s baseboard-serial-number"
        result = self._execute_command(command)
        if result and result.lower() not in ["", "null", "none", "not specified"]:
            return result

        command = "kenv -q smbios.planar.serial"
        result = self._execute_command(command)
        if result and result.lower() not in ["", "null", "none"]:
            return result

        command = "sysctl -n hw.serial"
        result = self._execute_command(command)
        if result and result.lower() not in ["", "null", "none"]:
            return result

        return "unknown"

    def _get_cpu_id(self) -> str:
        cpu_info = []

        cpu_keys = ["hw.model", "hw.machine", "hw.ncpu"]

        for key in cpu_keys:
            command = f"sysctl -n {key}"
            result = self._execute_command(command)
            if result:
                cpu_info.append(f"{key}={result}")

        if cpu_info:
            return " | ".join(cpu_info)

        command = "dmesg | grep -i cpu | head -1"
        result = self._execute_command(command)
        if result:
            return result.strip()

        return self.system_info.get("processor", "unknown")

    def _get_disk_serial(self) -> str:
        command = "camcontrol devlist"
        result = self._execute_command(command)
        if result:
            lines = result.split("\n")
            for line in lines:
                if "da0" in line or "ada0" in line:
                    return line.strip()

        command = "diskinfo -v /dev/ada0"
        result = self._execute_command(command)
        if result:
            for line in result.split("\n"):
                if "ident" in line.lower() or "serial" in line.lower():
                    parts = line.split()
                    if len(parts) >= 2:
                        return parts[-1]

        command = "dmesg | grep -i 'serial number' | head -1"
        result = self._execute_command(command)
        if result:
            return result.strip()

        return "unknown"

def get_platform_adapter() -> BasePlatformAdapter:
    system = platform.system().lower()

    if system == "windows":
        return WindowsPlatformAdapter()
    elif system == "linux":
        return LinuxPlatformAdapter()
    elif system == "darwin":
        return DarwinPlatformAdapter()
    elif system in ["freebsd", "openbsd", "netbsd"]:
        return BSDPlatformAdapter()
    else:
        raise PlatformNotSupported(f"不支持的平台: {system}")

class ConfigManager:
    DEFAULT_CONFIG = {
        "strategy": "auto",
        "format": "raw",
        "cache": {
            "enabled": True,
            "ttl": 3600,
            "file_cache": False,
            "cache_dir": tempfile.gettempdir(),
            "max_entries": 100,
        },
        "security": {"protected": False, "app_id": None},
        "fallback": {"enabled": True, "strategies": ["system", "hardware", "hybrid"]},
    }

    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self.config = self.DEFAULT_CONFIG.copy()

        if config_file and os.path.exists(config_file):
            self.load_config()

    def load_config(self) -> None:
        if not self.config_file or not os.path.exists(self.config_file):
            return

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                user_config = json.load(f)

            self._merge_config(self.config, user_config)

        except (IOError, json.JSONDecodeError):
            pass

    def save_config(self) -> None:
        if not self.config_file:
            return

        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)

            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)

        except (IOError, OSError):
            pass

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        keys = key.split(".")
        config = self.config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def _merge_config(self, base: dict, user: dict) -> None:
        for key, value in user.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value

class MachineIDGenerator:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config_manager = ConfigManager()
        if config:
            for key, value in config.items():
                self.config_manager.set(key, value)

        self.cache_manager = CacheManager(self.config_manager.get("cache", {}))
        self.platform_adapter = get_platform_adapter()

    def generate(
        self,
        strategy: Optional[str] = None,
        format_type: Optional[str] = None,
        app_id: Optional[str] = None,
    ) -> str:
        strategy = strategy or self.config_manager.get("strategy", "auto")
        format_type = format_type or self.config_manager.get("format", "raw")
        app_id = app_id or self.config_manager.get("security.app_id")

        cache_key = f"{strategy}_{format_type}_{app_id or 'none'}"

        cached_id = self.cache_manager.get(cache_key)
        if cached_id:
            return cached_id

        try:
            machine_id = self._generate_by_strategy(strategy)

            if not validate_machine_id(machine_id):
                if self.config_manager.get("fallback.enabled", True):
                    machine_id = self._generate_with_fallback(strategy)
                else:
                    raise MachineIDNotFound(f"生成的机器ID无效: {machine_id}")

            formatted_id = format_id(machine_id, format_type)

            if app_id:
                formatted_id = protect_id(app_id, formatted_id)

            self.cache_manager.set(cache_key, formatted_id)

            return formatted_id

        except Exception as e:
            if self.config_manager.get("fallback.enabled", True):
                return self._generate_with_fallback(strategy, format_type, app_id)
            else:
                raise e

    def _generate_by_strategy(self, strategy: str) -> str:
        if strategy == "auto":
            return self.platform_adapter.get_hybrid_id()
        elif strategy == "system":
            return self.platform_adapter.get_system_id()
        elif strategy == "hardware":
            return self.platform_adapter.get_hardware_id()
        elif strategy == "hybrid":
            return self.platform_adapter.get_hybrid_id()
        else:
            raise ValueError(f"不支持的策略: {strategy}")

    def _generate_with_fallback(
        self,
        original_strategy: str,
        format_type: Optional[str] = None,
        app_id: Optional[str] = None,
    ) -> str:
        fallback_strategies = self.config_manager.get(
            "fallback.strategies", ["system", "hardware", "hybrid"]
        )

        if original_strategy in fallback_strategies:
            fallback_strategies = [
                s for s in fallback_strategies if s != original_strategy
            ]

        for strategy in fallback_strategies:
            try:
                machine_id = self._generate_by_strategy(strategy)
                if validate_machine_id(machine_id):
                    formatted_id = format_id(machine_id, format_type or "raw")
                    if app_id:
                        formatted_id = protect_id(app_id, formatted_id)
                    return formatted_id
            except Exception:
                continue

        raise MachineIDNotFound("所有策略都无法生成有效的机器ID")

    def get_capabilities(self) -> Dict[str, Any]:
        return self.platform_adapter.get_capabilities()

    def clear_cache(self) -> None:
        self.cache_manager.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        return self.cache_manager.get_stats()

def id(
    strategy: str = "auto", format_type: str = "raw", app_id: Optional[str] = None
) -> str:
    generator = MachineIDGenerator()
    return generator.generate(strategy=strategy, format_type=format_type, app_id=app_id)

def protected_id(app_id: str, strategy: str = "auto", format_type: str = "raw") -> str:
    generator = MachineIDGenerator()
    return generator.generate(strategy=strategy, format_type=format_type, app_id=app_id)