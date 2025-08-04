import re
import uuid
from main import config


def http_attack(url):
    # sql注入, xss 远程命令执行，ddos，缓冲区溢出漏洞， 目录遍历， 未授权访问， 暴力破解...
    # sql注入漏洞利用特征
    pattern_sql = re.compile(
        r'(\=.*\-\-)'
        r'|(\w+(%|\$|#)\w+)'
        r'|(.*\|\|.*)'
        r'|(?:\s+(and|or)\s+)'
        r'|(\b(select|update|union|and|or|delete|insert|trancate|char|into|'
        r'substr|ascii|declare|exec)\b)'
        r'|(\b(count|master|drop|execute)\b)',
        re.IGNORECASE)
    """
    http://127.0.0.1/test.php?id=1 and (select count(*) from sysobjects)>0 and 1=1

    """
    # Cross-site scripting (XSS) attack vulnerability patterns
    pattern_xss = re.compile(
        r'(<.*>)'  # Match content surrounded by angle brackets
        r'|(\{|\})'  # Match left and right curly braces
        r'|"|>|<'  # Match quotes and angle brackets
        r'|(script)'  # Match 'script' keyword
        r'|(onerror)'  # Match 'onerror' keyword
        r'|(onload)'  # Match 'onload' keyword
        r'|(javascript:)'  # Match 'javascript:' keyword
        r'|(alert\()'  # Match 'alert()' keyword
        r'|(document\.)'  # Match 'document.' keyword
        r'|(window\.)'  # Match 'window.' keyword
        r'|(location\.)'  # Match 'location.' keyword
        r'|(eval\()'  # Match 'eval()' keyword
        r'|(setTimeout\()'  # Match 'setTimeout()' keyword
        r'|(setInterval\()',  # Match 'setInterval()' keyword
        re.IGNORECASE)
    # Command execution vulnerability patterns
    pattern_shell = re.compile(
        r"(eval)"
        r"|(ping)"
        r"|(echo)"
        r"|(cmd)"
        r"|(/etc/).+"
        r"|(whoami)"
        r"|(ipconfig)"
        r"|(/bin/).+"
        r"|(array_map)"
        r"|(phpinfo)"
        r"|(\$_).+"
        r"|(var_dump)"
        r"|(call_user_func)"
        r"|(/usr/).+"
        r"|(c:/).+", re.IGNORECASE)
    # Directory traversal patterns
    pattern_dir_search = re.compile(
        r'(/robots.txt)'  # Match robots.txt file
        r'|\.\./'  # Match ../ indicating parent directory
        r'|\w*.conf'  # Match files ending with .conf
        r'|(/admin)'  # Match /admin directory
        r'|(/etc/passwd)'  # Match /etc/passwd file
        r'|(/etc/shadow)'  # Match /etc/shadow file
        r'|(/etc/hosts)'  # Match /etc/hosts file
        r'|(/etc/group)'  # Match /etc/group file
        r'|(/proc/version)'  # Match /proc/version file
        r'|(/proc/self/environ)'  # Match /proc/self/environ file
        r'|(/proc/cmdline)'  # Match /proc/cmdline file
        r'|(/proc/mounts)'  # Match /proc/mounts file
        r'|(/proc/net/route)',  # Match /proc/net/route file
        re.IGNORECASE)
    # Deserialization vulnerability patterns
    pattern_serialize = re.compile(
        r"(‘/[oc]:\d+:/i’, \$var)"  # Match specific format deserialization strings
        r'|(unserialize\()'  # Match 'unserialize()' function
        r'|(base64_decode\()'  # Match 'base64_decode()' function
        r'|(json_decode\()'  # Match 'json_decode()' function
        r'|(msgpack_unpack\()'  # Match 'msgpack_unpack()' function
        r'|(pickle.loads\()'  # Match 'pickle.loads()' function
        r'|(xmlrpc_decode\()',  # Match 'xmlrpc_decode()' function
        re.IGNORECASE)
    pattern_url_file_inclusion = re.compile(
        r'(\binclude\b)'
        r'|(\brequire\b)'
        r'|(\brequire_once\b)'
        r'|(\binclude_once\b)',  # Match file inclusion vulnerability keywords in URL
        re.IGNORECASE
    )
    patterns = {
        'sql': pattern_sql,
        'xss': pattern_xss,
        'shell': pattern_shell,
        'dir_search': pattern_dir_search,
        'serialize': pattern_serialize
    }
    for pattern_name, pattern in patterns.items():
        match = pattern.search(url)
        if match is not None:
            attack, threat = config.get_risk_level(pattern_name)
            attack_name = pattern_name
            feature = match[0]
            break
        else:
            attack = threat = feature = attack_name = None

    return (attack, attack_name), threat, feature


def generate_task_id():
    return str(uuid.uuid4())
