package sir.io;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HexFormat;

/** Huellas para detectar cambios en la pareja de CSV, sin cargar los archivos en memoria. */
public final class HuellasArchivos {
    private HuellasArchivos() { }

    static MessageDigest nuevaHuella() {
        try {
            return MessageDigest.getInstance("SHA-256");
        } catch (NoSuchAlgorithmException error) {
            throw new IllegalStateException("El JDK debe proporcionar SHA-256.", error);
        }
    }

    public static String calcular(Path archivo) throws IOException {
        MessageDigest huella = nuevaHuella();
        try (InputStream entrada = Files.newInputStream(archivo)) {
            byte[] bloque = new byte[8192];
            int cantidad;
            while ((cantidad = entrada.read(bloque)) != -1) {
                huella.update(bloque, 0, cantidad);
            }
        }
        return HexFormat.of().formatHex(huella.digest());
    }
}
