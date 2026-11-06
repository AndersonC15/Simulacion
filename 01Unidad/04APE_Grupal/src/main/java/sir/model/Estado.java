package sir.model;

public enum Estado {

    SUSCEPTIBLE("S", "Susceptibles"),
    INFECTADO("I", "Infectados"),
    RECUPERADO("R", "Recuperados");

    private final String abreviatura;
    private final String nombre;

    Estado(String abreviatura, String nombre) {
        this.abreviatura = abreviatura;
        this.nombre = nombre;
    }

    public String getAbreviatura() {
        return abreviatura;
    }

    public String getNombre() {
        return nombre;
    }
}
