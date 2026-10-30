import com.google.gson.*;
import com.mojang.serialization.JsonOps;
import net.minecraft.server.packs.metadata.pack.PackFormat;
import net.minecraft.server.packs.PackType;
import java.util.zip.*;
public class PackCheck {public static void main(String[] args)throws Exception{try(var zip=new ZipFile(args[0])){var reader=new java.io.InputStreamReader(zip.getInputStream(zip.getEntry("pack.mcmeta")));var pack=JsonParser.parseReader(reader).getAsJsonObject().get("pack");System.out.println(PackFormat.packCodec(PackType.CLIENT_RESOURCES).codec().parse(JsonOps.INSTANCE,pack).getOrThrow());}}}
