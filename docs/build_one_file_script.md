- given a .py module file (start with challenge 's main file) :
  - save the content of the file without import statements (Body)
  - get all import statements
      - get type of import statement (Import & ImportFrom), check for aliases
      - list imported packages & modules
      - are modules present locally (from botlibs / challengelibs packages) ?
        - yes :
          - throw an exception if imported with Import (for now)
          - do the same with module's file
        - no : stop


- create <challenge_name>.py destination file (destroy if already exists) and open it :
    - given all import statements :
      - if not local : append to destination file
      - if Import from local module : throw an exception (for now)
    - given all Script's modules content (copy only once) :
      - append to destination file
    - scan built file import statements : remove duplicates
