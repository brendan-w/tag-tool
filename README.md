tag-tool
========

CLI for organizing files in a tag-based fashion

A simple case:

```shell
$ tree
.
└── a_b_c.txt

$ tag -b a_b_c.txt

$ tree
.
└── a_c.txt
```

A more complex case:

```shell
$ tree -a
.
├── .tagdir
├── a/
└── d_e/
    └── file.txt

$ tag -d +z d_e/file.txt

$ tree -a
.
├── .tagdir
├── a/
│   └── e_z_file.txt
└── d_e/
```
