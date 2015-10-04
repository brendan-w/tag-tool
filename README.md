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
$ tree
.
├── a/
└── d_e/
    └── a_b_c.txt

$ tag -d +z d_e/a_b_c.txt

$ tree
.
├── a/
│   └── e_z_b_c.txt
└── d_e/
```
