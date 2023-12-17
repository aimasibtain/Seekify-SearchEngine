package com.mycompany.invertedindex;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.File;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

public class barrels {
    private static Map<String, Map<String, Integer>>[] createBarrels(Map<String, Map<String, Integer>> invertedIndex, int numBarrels) {
        // Initialize barrels
        Map<String, Map<String, Integer>>[] barrels = new HashMap[numBarrels];
        for (int i = 0; i < numBarrels; i++) {
            barrels[i] = new HashMap<>();
        }

        // Iterate through each term in the inverted index
        for (Map.Entry<String, Map<String, Integer>> entry : invertedIndex.entrySet()) {
            // Assign each term to a barrel based on a simple hash function
            int barrelIndex = Math.abs(entry.getKey().hashCode()) % numBarrels;

            // Add the term and its document frequencies to the corresponding barrel
            barrels[barrelIndex].put(entry.getKey(), entry.getValue());
        }

        return barrels;
    }
    
    public static void main(String[] args) {
         String filePath = "inverted_index.json";

         
           try {
            // Create an ObjectMapper instance
            ObjectMapper objectMapper = new ObjectMapper();

            // Read data from the file into a Map
           
        // Read and store data from the file
        Map<String, Map<String, Integer>> invertedIndexData= objectMapper.readValue(new File(filePath), Map.class);
       

                // Number of barrels
        int numBarrels = 150;

        // Create barrels
        Map<String, Map<String, Integer>>[] barrels = createBarrels(invertedIndexData, numBarrels);
        
        for (int i = 0; i < numBarrels; i++) {
            try {
                objectMapper.writerWithDefaultPrettyPrinter().writeValue(new File("barrel_" + (i + 1) + ".json"), barrels[i]);
                
                System.out.println("Barrel " + (i + 1) + "\n");
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
                       catch (IOException e) {
        }
}
}