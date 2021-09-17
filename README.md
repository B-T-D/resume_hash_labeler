# resume_hash_labeler


### Desired command line syntax

* Generate new hash label and print it to command line:

        <executable call>  // I.e. run the executable with no other arguments

* Print the full filename to the command line--"Name_resume_abc123.docx". Supported for any command that results in printing the label to the terminal:

        <executable call> <optional command> -fn
  
* Specify value for "genre" field of a new label:

        <executable call> -g"valid genre field"

* Specify value for the "note" field of a new label:

        <executable call> -n"my note field"
