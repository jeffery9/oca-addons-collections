import json
import argparse
import os
import shutil
from pathlib import Path


def remove_newline(string):

    return string.replace('\n', '')


def list_modules():

    path = r"."
    top_dirs = os.listdir(path)

    _app = {}
    __app = {}
    for dir in top_dirs:
        _path = os.path.join(path, dir)

        apps = []

        if os.path.isdir(_path):
            for _dir in os.listdir(_path):
                if '_release' in dir:
                    continue

                __path = os.path.join(_path, _dir)
                if os.path.isdir(__path):
                    manifest = os.path.join(__path, r"__manifest__.py")
                    if os.path.isfile(manifest):

                        _m_dict = eval(open(manifest).read())

                        summary = remove_newline(_m_dict.get("summary", ""))
                        apps.append(_dir)
                        __app.update(
                            {
                                _dir: {
                                    "project": dir,
                                    "summary": summary,
                                    "version": _m_dict.get("version", ""),
                                    "depends": _m_dict.get("depends", []),
                                    "development_status": _m_dict.get("development_status", 'Unkown'),
                                }
                            }
                        )

        _app.update({dir: apps})

    _app.update({".index": __app})

    return _app


def find_all_modules(dependencies_json, start_module, all_modules=None):
    """
    递归查找所有模块。
    参数:
    dependencies_json (dict): 模块依赖关系的 JSON 对象。
    start_module (str): 起始模块的名称。
    all_modules (set): 存储所有模块的集合。
    返回:
    set: 所有模块的集合。
    """
    if all_modules is None:
        all_modules = set()

    all_modules.add(start_module)

    if start_module in dependencies_json:
        for dependency in dependencies_json[start_module]['depends']:
            if dependency not in all_modules:
                find_all_modules(dependencies_json, dependency, all_modules)

    return all_modules


def find_all_modules_no_start(dependencies_json):
    all_modules = set()
    for module in dependencies_json:
        all_modules.add(module)
        for dependency in dependencies_json[module]:
            all_modules.add(dependency)
    return all_modules


def create_release(module_list, dependencies_data, NOCACHE):
    try:
        os.makedirs('_release', exist_ok=True)
        if NOCACHE:
            print(f">>> 清理目录 _release/")
            shutil.rmtree('_release/')
        for module in module_list:
            destination_dir = f'_release/{module}'
            dependency = dependencies_data.get(module)
            print('>>> ', module)
            if dependency:
                project = dependency['project']
                path = f'{project}/{module}'
                print('    found ', path)

                if os.path.exists(destination_dir):
                    shutil.rmtree(destination_dir)
                shutil.copytree(path, destination_dir)
                print('    copied')

            else:
                print('    not found')
    except Exception as e:
        print(f"发生错误：{e}")


if __name__ == "__main__":
    # 创建参数解析器
    parser = argparse.ArgumentParser(description="查找模块依赖关系。")
    parser.add_argument("app", help="起始模块的名称。")
    parser.add_argument("--no_cache", help="是否清空 _relase 目录。", default=False, action='store_true')

    # 解析命令行参数
    args = parser.parse_args()
    APP = args.app
    NOCACHE = args.no_cache

    catalog = list_modules()
    dependencies_data = catalog.get('.index')

    if dependencies_data:
        if APP:
            if dependencies_data.get(APP, False):
                print(f">>> App {APP}")
                all_modules = set()
                # 查找所有模块
                modules = find_all_modules(dependencies_data, APP)
                # 打印结果
                print(">>> found modules:", modules)
                all_modules.update(modules)

                create_release(all_modules, dependencies_data, NOCACHE)

                print(">>> done.")