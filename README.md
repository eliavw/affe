# affe

AFFE is short for 
**A**nother 
**F**ramework 
**F**or 
**E**xperiments.

There are _many_ experimental frameworks out there (hence the `A` in `AFFE`), but `AFFE` still got built because what we wanted to do did not really exist yet.

## Description

In a nutshell, `AFFE` is simple and modular. You import it as a python package, and you get access to a bunch of functions that may alleviate some technical tasks that pop up when doing experiments at scale.
Examples include proper logging, or defining composite experiments (called 'workflows' in affe). 

These are things that are not necessarily hard to do, but if you want to do them right, things can become tedious quickly. Therefore, in developing `AFFE`, the idea is to get those things right, spend a bit more time in making it generalizable and clean, and then never have to do them ever again.

## Usage

For a local install, `cd` to the root of this repository and simply; 

```
python setup.py develop
```

## Documentation

Soon...

## Administration

Open the folder [note/deploy](./note/deploy) for notebooks that contain annotated scripts for the different administrative tasks you may want to undertake with this software project.
