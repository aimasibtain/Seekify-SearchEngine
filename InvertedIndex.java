package com.mycompany.invertedindex;
import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import org.json.JSONObject;

public class InvertedIndex {

    public static void main(String[] args) throws IOException{
 String file_path = "D:\\3rd Semester\\DSA\\PROJECTT\\forward_index.json";

        try {
            //Buffered Reader to read content of file 
            //File Reader just to access file or load file
            try (BufferedReader reader = new BufferedReader(new FileReader(file_path))) {
         
                StringBuilder forward_index = new StringBuilder();
                String line;

                while ((line = reader.readLine()) != null) { //Loop to read data line by line
                    forward_index.append(line);//json
                }

                //creating json object
                JSONObject json_file = new JSONObject(forward_index.toString());

                // Accessing the data from the JSON object (DOcument ids)
                JSONObject documents = json_file.getJSONObject("documents");
                Map<String,Set<Integer>> Inverted_index =new HashMap<>();
                // Iterate through document IDs
                for (String documentId : documents.keySet()) {                    
                    JSONObject words = documents.getJSONObject(documentId).getJSONObject("words");
                    // Iterate through word IDs
                    for (String wordId : words.keySet()) {
                        if (Inverted_index == null) {
                            System.out.println("inverted_index is null");
                        } else {
                         //computeIfAbsent with null check--> so that map must have value for each wordId
                             Inverted_index.computeIfAbsent(wordId, k -> new HashSet<>()).add(Integer.valueOf(documentId));
                             System.out.println("WordId: "+wordId);
                             System.out.println("DocumentId:  "+documentId);
                        }
                    }
                }

            }
        
        } catch (FileNotFoundException e) {
            System.out.println(e.getMessage()+"Unable to open Forward index file");
          }
        
        
   }
}
