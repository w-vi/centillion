# centillion

**the centillion**: a pan-github-markdown-issues-google-docs search engine.

**a centillion**: a very large number consisting of a 1 with 303 zeros after it.

the centillion is 3.03 log-times better than the googol.



## where we are at

Current status:

* Successfully using whoosh to index a directory of Markdown files
    * Problem: .git directory cannot be present (or contaminates list of
      indexed directories)
    * Problem: search index stored on disk, not clear how to use on Heroku
    * may need to check in binary search index, or dive headfirst into
          sqlalchemy
    * not using pandoc to extract header/emphasis information

Needs work:

* More appropriate schema
* Using more features (weights) plus pandoc filters for schema
* sqlalchemy (and hey waddya know safari books has it covered)


## how it will work

the centillion uses whoosh, a python library for building
search engines. 

the centillion creates a schema to index our different items,
and then we add documents to it. whoosh requires lots of
configurations of how we want to index each of our items.

the centillion keeps it simple.


### folder of markdown files

The first type of document collection that the centillion
can handle is a folder with markdown files in it.

the centillion will walk the directory and sniff out
markdown files. it will then use pandoc to extract information
from the markdown documents. 

all markdown documents in the folders will be added to
the index.


### github issues

The next type of document collection that the centillion
can handle is a collection of github issues from a 
repository.

the centillion will extract information from the 
issues and comments using PyGithub and use pandoc
to extract information from the markdown in the
issues/comments.

all issues and comments in the repo will be added to
the index.


### google drive

the last type of document collection that the centillion
can handle is a google drive folder. the google drive
API allows the centillion to download documents in multiple
formats (primarily the .docx format), convert to markdown,
and extract information as was done with github
markdown files.



