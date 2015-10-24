tag-tool
========

CLI for organizing files in a tag-based fashion

A simple case:

```shell
$ ls
a_file

$ tag +z -a a_file

$ ls
z_file
```

A more complex case:

```shell
$ tree -a
.
├── .tagdir
├── a/
└── some_dir/
    └── a_file

$ tag -dir some_dir/a_file

$ tree -a
.
├── .tagdir
├── a/
│   └── some_file
└── some_dir/
```
