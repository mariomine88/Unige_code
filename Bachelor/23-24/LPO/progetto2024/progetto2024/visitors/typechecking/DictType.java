package progetto2024.visitors.typechecking;

import static java.util.Objects.requireNonNull;

public record DictType(Type valueType) implements Type {

    public static final String TYPE_NAME = "DICT";

    public DictType {
        requireNonNull(valueType);
    }

    @Override
    public String toString() {
        return String.format("%s DICT", valueType);
    }
}