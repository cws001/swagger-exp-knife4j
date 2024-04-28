import argparse

from lib import console, description
from lib.console import SpringBoot_Exp_console


def get_parser():
    parser = argparse.ArgumentParser(usage='python3 swagger-exp-knife4j.py',description='swagger-exp-knife4j: 针对swagger的开源渗透框架',)
    p = parser.add_argument_group('SpringBoot-Scan 的参数')
    p.add_argument("-u", "--url", type=str, help="对单一URL")
    p.add_argument("-c", "--chrome", action='store_true', help="open chrome")
    args = parser.parse_args()
    return args

def main():
    description.logo()
    description.usage()
    args = get_parser()
    SpringBoot_Exp_console(args)
    # console.SpringBoot_Exp_console(args)

if __name__ == '__main__':
    main()
