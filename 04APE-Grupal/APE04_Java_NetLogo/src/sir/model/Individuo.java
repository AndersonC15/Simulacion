package sir.model;

public class Individuo {

    private final int id;
    private Estado estado;

    public Individuo(int id, Estado estado) {
        this.id = id;
        this.estado = estado;
    }

    public int getId() {
        return id;
    }

    public Estado getEstado() {
        return estado;
    }

    public void setEstado(Estado estado) {
        this.estado = estado;
    }
}
