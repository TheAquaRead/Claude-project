package ru.prisonevo;

import org.bukkit.configuration.file.YamlConfiguration;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

/** One atomic snapshot: an allocation is persisted before its island is built. */
final class IslandStore {
    private final File file;
    private final int grid; private final String worldName;
    final Map<UUID,IslandData> players=new HashMap<>();
    int nextIndex=0;
    IslandStore(File folder,int grid,String worldName){file=new File(folder,"islands.yml");this.grid=grid;this.worldName=worldName;}
    void load() throws Exception {
        if(!file.exists())return;
        YamlConfiguration y=new YamlConfiguration(); y.load(file);
        if(y.getInt("grid-size",-1)!=grid || !worldName.equals(y.getString("world"))) throw new IOException("World name or grid size changed; migration required");
        nextIndex=y.getInt("next-index",0);
        var section=y.getConfigurationSection("players"); if(section==null)return;
        Set<Integer> indices=new HashSet<>();
        for(String key:section.getKeys(false)){
            UUID id=UUID.fromString(key);String p="players."+key+".";
            int index=y.getInt(p+"index",-1); if(index<0||!indices.add(index))throw new IOException("Invalid or duplicate island index: "+index);
            IslandData d=new IslandData(id,index); d.built=y.getBoolean(p+"built");
            d.speed=Math.clamp(y.getInt(p+"speed",1),1,10);d.power=Math.clamp(y.getInt(p+"power",1),1,10);
            d.storage=Math.clamp(y.getInt(p+"storage",1),1,10);d.mine=Math.clamp(y.getInt(p+"mine",1),1,10);
            d.balance=Math.max(0,y.getLong(p+"balance"));d.stored=Math.max(0,y.getLong(p+"stored"));
            d.lastTick=y.getLong(p+"last-tick",System.currentTimeMillis());d.resetAt=y.getLong(p+"reset-at");
            d.returnWorld=y.getString(p+"return.world");d.returnX=y.getDouble(p+"return.x");d.returnY=y.getDouble(p+"return.y");d.returnZ=y.getDouble(p+"return.z");
            d.returnYaw=(float)y.getDouble(p+"return.yaw");d.returnPitch=(float)y.getDouble(p+"return.pitch");
            players.put(id,d);nextIndex=Math.max(nextIndex,index+1);
        }
    }
    void save() throws IOException {
        YamlConfiguration y=new YamlConfiguration();y.set("world",worldName);y.set("grid-size",grid);y.set("next-index",nextIndex);
        for(IslandData d:players.values()){
            String p="players."+d.owner+".";y.set(p+"index",d.index);y.set(p+"built",d.built);
            y.set(p+"speed",d.speed);y.set(p+"power",d.power);y.set(p+"storage",d.storage);y.set(p+"mine",d.mine);
            y.set(p+"balance",d.balance);y.set(p+"stored",d.stored);y.set(p+"last-tick",d.lastTick);y.set(p+"reset-at",d.resetAt);
            if(d.returnWorld!=null){y.set(p+"return.world",d.returnWorld);y.set(p+"return.x",d.returnX);y.set(p+"return.y",d.returnY);y.set(p+"return.z",d.returnZ);y.set(p+"return.yaw",d.returnYaw);y.set(p+"return.pitch",d.returnPitch);}
        }
        Files.createDirectories(file.toPath().getParent());
        Path tmp=Files.createTempFile(file.toPath().getParent(),"islands-", ".tmp");
        try {
            Files.writeString(tmp,y.saveToString(),StandardCharsets.UTF_8);
            try{Files.move(tmp,file.toPath(),StandardCopyOption.REPLACE_EXISTING,StandardCopyOption.ATOMIC_MOVE);}
            catch(AtomicMoveNotSupportedException ex){Files.move(tmp,file.toPath(),StandardCopyOption.REPLACE_EXISTING);}
        }finally{Files.deleteIfExists(tmp);}
    }
}
