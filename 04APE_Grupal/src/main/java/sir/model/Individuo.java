package sir.model;

public final class Individuo {

    private final int id;
    private Estado estado;

    public Individuo(int id, Estado estado) {
        if (id < 0) { throw new IllegalArgumentException("ID negativo."); }
        this.id = id;
        setEstado(estado);
    }

    public int getId() {
        return id;
    }

    public Estado getEstado() {
        return estado;
    }

    public void setEstado(Estado estado) {
        this.estado = java.util.Objects.requireNonNull(estado, "El estado no puede ser null.");
    }
}
