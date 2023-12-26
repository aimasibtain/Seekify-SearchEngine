package com.mycompany.invertedindex;
import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.json.JSONArray;
import org.json.JSONObject;

public class InvertedIndex {

    public static void main(String[] args) throws IOException {

        String file_path = "forward_index.json";

        try (BufferedReader reader = new BufferedReader(new FileReader(file_path))) {

            StringBuilder forward_index = new StringBuilder();
            String line;

            while ((line = reader.readLine()) != null) {
                forward_index.append(line);
            }

            JSONObject json_file = new JSONObject(forward_index.toString());
            JSONObject documents = json_file.getJSONObject("documents");
            Map<String, Map<String, Map<String, List<Integer>>>> inverted_index = new HashMap<>();

            for (String documentId : documents.keySet()) {
                JSONObject document = documents.getJSONObject(documentId);
                JSONObject words = document.getJSONObject("words");

                for (String wordId : words.keySet()) {
                    JSONObject wordInfo = words.getJSONObject(wordId);
                    int frequency = wordInfo.getInt("frequency");
                    JSONArray positionsArray = wordInfo.getJSONArray("positions");

                        for (int i = 0; i < positionsArray.length(); i++) {
                          JSONArray position = positionsArray.getJSONArray(i);
                           int positionValue = position.getInt(0);

                            inverted_index
                            .computeIfAbsent(wordId, k -> new HashMap<>())
                            .computeIfAbsent(documentId, k -> new HashMap<>())
                            .computeIfAbsent("positions", k -> new ArrayList<>())
                            .add(positionValue);
}
                }
            }

            JSONObject invertedIndexJson = new JSONObject(inverted_index);

            try (FileWriter index_write = new FileWriter("inverted_index.json")) {
                index_write.write(invertedIndexJson.toString(4));
                System.out.println("Data written on inverted-index file");
            } catch (IOException e) {
                System.out.println("ERROR! " + e.getMessage());
            }

        } catch (FileNotFoundException e) {
            System.out.println(e.getMessage() + " Unable to access Forward index file");
        }
    }
}

