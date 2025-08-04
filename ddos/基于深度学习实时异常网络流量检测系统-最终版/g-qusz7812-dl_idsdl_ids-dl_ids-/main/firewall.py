import subprocess
import platform
import re


class FirewallManager:
    @staticmethod
    def is_valid_ip(ip):
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(pattern, ip):
            return False
        octets = ip.split('.')
        return all(0 <= int(octet) <= 255 for octet in octets)

    @staticmethod
    def add_rule(ip, rule_type):
        """添加防火墙规则"""
        if not FirewallManager.is_valid_ip(ip):
            raise ValueError("Invalid IP address")

        system = platform.system().lower()

        try:
            if system == 'windows':
                print(f"rule_type: {rule_type}, ip: {ip}, system: {system}")
                if rule_type == 'black':
                    # 添加入站规则
                    subprocess.run([
                        'netsh', 'advfirewall', 'firewall', 'add', 'rule',
                        'name=BlockIP_{}'.format(ip),
                        'dir=in', 'action=block',
                        'remoteip={}'.format(ip)
                    ], check=True)
                    # 添加出站规则
                    subprocess.run([
                        'netsh', 'advfirewall', 'firewall', 'add', 'rule',
                        'name=BlockIP_{}'.format(ip),
                        'dir=out', 'action=block',
                        'remoteip={}'.format(ip)
                    ], check=True)
                else:  # white
                    # 添加入站允许规则
                    subprocess.run([
                        'netsh', 'advfirewall', 'firewall', 'add', 'rule',
                        'name=AllowIP_{}'.format(ip),
                        'dir=in', 'action=allow',
                        'remoteip={}'.format(ip)
                    ], check=True)
                    # 添加出站允许规则
                    subprocess.run([
                        'netsh', 'advfirewall', 'firewall', 'add', 'rule',
                        'name=AllowIP_{}'.format(ip),
                        'dir=out', 'action=allow',
                        'remoteip={}'.format(ip)
                    ], check=True)

            elif system == 'linux':
                print(f"rule_type: {rule_type}, ip: {ip}, system: {system}")
                if rule_type == 'black':
                    subprocess.run(['iptables', '-A', 'INPUT', '-s', ip, '-j', 'DROP'], check=True)
                    subprocess.run(['iptables', '-A', 'OUTPUT', '-d', ip, '-j', 'DROP'], check=True)
                else:  # white
                    subprocess.run(['iptables', '-A', 'INPUT', '-s', ip, '-j', 'ACCEPT'], check=True)
                    subprocess.run(['iptables', '-A', 'OUTPUT', '-d', ip, '-j', 'ACCEPT'], check=True)

            return True
        except subprocess.CalledProcessError as e:
            print(f"Error adding firewall rule: {e}")
            return False

    @staticmethod
    def remove_rule(ip, rule_type):
        """删除防火墙规则"""
        if not FirewallManager.is_valid_ip(ip):
            raise ValueError("Invalid IP address")

        system = platform.system().lower()

        try:
            if system == 'windows':
                rule_name = 'BlockIP_{}' if rule_type == 'black' else 'AllowIP_{}'
                subprocess.run([
                    'netsh', 'advfirewall', 'firewall', 'delete', 'rule',
                    'name={}'.format(rule_name.format(ip))
                ], check=True)

            elif system == 'linux':
                if rule_type == 'black':
                    subprocess.run(['iptables', '-D', 'INPUT', '-s', ip, '-j', 'DROP'], check=True)
                    subprocess.run(['iptables', '-D', 'OUTPUT', '-d', ip, '-j', 'DROP'], check=True)
                else:  # white
                    subprocess.run(['iptables', '-D', 'INPUT', '-s', ip, '-j', 'ACCEPT'], check=True)
                    subprocess.run(['iptables', '-D', 'OUTPUT', '-d', ip, '-j', 'ACCEPT'], check=True)

            return True
        except subprocess.CalledProcessError as e:
            print(f"Error removing firewall rule: {e}")
            return False
