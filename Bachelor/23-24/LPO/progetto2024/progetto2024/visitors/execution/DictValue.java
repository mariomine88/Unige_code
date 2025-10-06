package progetto2024.visitors.execution;

import static java.util.Objects.hash;
import static java.util.Objects.requireNonNull;
import java.util.TreeMap;

public class DictValue implements Value {

    private final TreeMap<Integer, Value> dict;

    public DictValue(Integer key, Value value) {
        this.dict = new TreeMap<>();
        this.dict.put(key, value);
    }

    public DictValue(TreeMap<Integer, Value> dict) {
        this.dict = new TreeMap<>(dict);
    }
    
    @Override
    public DictValue toDict() {
        return this;
    }
    
    public TreeMap<Integer, Value> getDict() {
        return dict;
    }

    public TreeMap<Integer, Value> put(Integer key, Value value) {
        requireNonNull(key, "Key cannot be null");
        requireNonNull(value, "Value cannot be null");
        dict.put(key, value);
        return dict;
    }

    private void checkKey(Integer key) {
        requireNonNull(key, "Key cannot be null");
        if(!this.dict.containsKey(key))
            throw new InterpreterException("Missing key " + (key));
    }

    public Value get(Integer key) {
        checkKey(key);
        return dict.get(key);
    }

    
    public TreeMap<Integer, Value> remove(Integer key) {
        checkKey(key);
        dict.remove(key);
        return dict;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("[");
        dict.forEach((key, value) -> sb.append(key).append(":").append(value).append(","));
        if (!dict.isEmpty()) {
            sb.setLength(sb.length() - 1); // Remove the last comma
        }
        sb.append("]");
        return sb.toString();
    }

    @Override
    public int hashCode() {
        return hash(dict);
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj)
            return true;
        if (obj instanceof DictValue dv)
            return dict.equals(dv.dict);
        return false;
    }
}