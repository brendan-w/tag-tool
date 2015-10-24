tag-tool
========

CLI for organizing files in a tag-based fashion

A simple case:

```shell
a_file

$ tag +z -a a_file

z_file
```

A more complex case:

```shell
.
├── .tagdir
├── a/
└── some_dir/
    └── a_file

$ tag -dir some_dir/a_file

.
├── .tagdir
├── a/
│   └── some_file
└── some_dir/
```
