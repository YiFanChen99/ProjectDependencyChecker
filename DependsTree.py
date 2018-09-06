#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Accessor.JsonAccessor import *


tree_file = "./Tree.json"
tree_last_file = "./TreeLast.json"


class DependsTree(object):
    def __init__(self, file_path=None, data=None):
        self.projects_checked = set()
        self.projects_unchecked = set()
        self.projects = {}

        if file_path is not None:
            self.load(file_path)
        elif data is not None:
            self._init_by_data(data)

    def _init_by_data(self, data):
        self.projects_checked = set(data['projects_checked'])
        self.projects_unchecked = set(data['projects_unchecked'])
        self.projects = data['projects']

    def load(self, file_path):
        data = load_json(file_path)
        self._init_by_data(data)

    def save(self, file_path):
        data = {
            'projects_checked': list(self.projects_checked),
            'projects_unchecked': list(self.projects_unchecked),
            'projects': self.projects
        }
        save_json(file_path, data)

    def add_depends(self, project, depends):
        if project in self.projects_checked:
            raise ValueError("{0} already in checked list.".format(project))

        self.projects[project] = depends
        for depend_unchecked in [each_depend for each_depend in depends if each_depend not in self.projects_checked]:
            self.projects_unchecked.add(depend_unchecked)

        self.projects_checked.add(project)
        self.projects_unchecked.discard(project)

    def get_next_unchecked(self, count):
        if count >= len(self.projects_unchecked):
            return list(self.projects_unchecked)

        next_unchecked = []
        for i in range(0, count):
            next_unchecked.append(self.projects_unchecked.pop())
        self.projects_unchecked.update(next_unchecked)
        return next_unchecked

    def get_statistics(self):
        return len(self.projects_checked), len(self.projects_unchecked)


def form_new_last(tree=None):
    if tree is None:
        tree = DependsTree(file_path=tree_file)

    next_one = tree.get_next_unchecked(1)
    checked, unchecked = tree.get_statistics()
    return {
        "Next": next_one[0] if next_one else None,
        "Checked": checked,
        "Unchecked": unchecked
    }


def add_depends(project, depends):
    tree = DependsTree(file_path=tree_file)
    tree.add_depends(project, depends)
    tree.save(tree_file)

    return form_new_last(tree)


def add_depends_for_next(depends):
    old_last = load_json(tree_last_file)
    new_last = add_depends(old_last['Next'], depends)
    save_json(tree_last_file, new_last)

    print_results(old_last, new_last)


def print_results(old_last, new_last):
    last_checked = old_last['Checked']
    last_unchecked = old_last['Unchecked']
    new_checked = new_last['Checked']
    new_unchecked = new_last['Unchecked']
    print("Added: {6}, Checked: {0}->{1} ({2}), Unchecked: {3}->{4} ({5})".format(
        last_checked, new_checked, new_checked- last_checked,
        last_unchecked, new_unchecked, new_unchecked - last_unchecked,
        old_last['Next']
    ))
    next_one = new_last['Next']
    print("Next: {0} has copied to the clipboard.".format(next_one))
    copy_to_clipboard("cat {0}/SynoBuildConf/".format(next_one))


def check_inconsistency():
    tree = DependsTree(tree_file)
    checked = tree.projects_checked
    projects = set(tree.projects)

    checked_only = checked.copy()
    checked_only.difference_update(projects)
    projects_only = projects.copy()
    projects_only.difference_update(checked)

    if len(checked_only) != 0 or len(projects_only) != 0:
        print("checked_only: ", checked_only)
        print("projects_only: ", projects_only)
        raise ValueError("Inconsistently!")
    else:
        print("Consistently.")


def copy_to_clipboard(string):
    import subprocess
    subprocess.run(['clip.exe'], input=string.strip().encode('utf-8'), check=True)


def update_last_next():
    old_last = load_json(tree_last_file)
    new_last = form_new_last()
    save_json(tree_last_file, new_last)

    print_results(old_last, new_last)


ddepends = [
"FirstDep",
"SecondDep"
]

add_depends_for_next(ddepends)
# update_last_next()

# check_inconsistency()
