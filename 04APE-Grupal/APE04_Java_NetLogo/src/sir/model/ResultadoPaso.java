package sir.model;

public class ResultadoPaso {

    private final int tiempo;
    private final int susceptibles;
    private final int infectados;
    private final int recuperados;

    public ResultadoPaso(int tiempo, int susceptibles, int infectados, int recuperados) {
        this.tiempo = tiempo;
        this.susceptibles = susceptibles;
        this.infectados = infectados;
        this.recuperados = recuperados;
    }

    public int getTiempo() {
        return tiempo;
    }

    public int getSusceptibles() {
        return susceptibles;
    }

    public int getInfectados() {
        return infectados;
    }

    public int getRecuperados() {
        return recuperados;
    }

    public int getTotal() {
        return susceptibles + infectados + recuperados;
    }

    public String aCsv() {
        return tiempo + "," + susceptibles + "," + infectados + "," + recuperados;
    }
}
