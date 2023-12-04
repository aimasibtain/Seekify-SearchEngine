
package com.mycompany.invertedindex;
import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import org.json.JSONObject;

public class InvertedIndex {

    public static void main(String[] args) throws IOException{
        
 String file_path = "forward_index.json";

        try{
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
                Map<String,Map<String,Integer>> Inverted_index =new HashMap<>();
                // Iterate through document IDs
                for (String documentId : documents.keySet()) {                    
                    JSONObject words = documents.getJSONObject(documentId).getJSONObject("words");
                    System.out.println("DOcument id: "+documentId);
                    // Iterate through word IDs
                
                    for (String wordId : words.keySet()) {
                        if (Inverted_index == null) {
                            System.out.println("inverted_index is null");
                        } else {
                         //computeIfAbsent with null check--> so that map must have value for each wordId
                         
                        // Get the frequency of the word in the current document// Assuming Inverted_index is declared as Map<String, Map<String, Integer>>
                    int frequency = words.getJSONObject(wordId).getInt("frequency");

                    Inverted_index.computeIfAbsent(wordId, k -> new HashMap<>()).put(documentId, frequency);

//                    For inverted index without frequency:
//                             Inverted_index.computeIfAbsent(wordId, k -> new HashSet<>()).add(Integer.valueOf(documentId));
                        }
                    }
                }
                
            //Conversion of map into Json object 
            JSONObject Inverted_Index=new JSONObject(Inverted_index);

            try (FileWriter index_write = new FileWriter("inverted_index.json")) {
                index_write.write(Inverted_Index.toString(4));
                System.out.println("Data written on index file");
            } catch (IOException e) {
                System.out.println("ERROR! " + e.getMessage());
            } 
            }
        } catch (FileNotFoundException e) {
            System.out.println(e.getMessage()+"Unable to access Forward index file");
          }  
    }
}
