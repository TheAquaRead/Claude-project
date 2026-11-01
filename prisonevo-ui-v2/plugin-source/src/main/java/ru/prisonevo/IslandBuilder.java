package ru.prisonevo;

import org.bukkit.*;
import org.bukkit.block.Block;
import org.bukkit.block.data.BlockData;
import org.bukkit.generator.ChunkGenerator;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.scheduler.BukkitRunnable;
import java.util.*;
import java.util.function.Consumer;
import java.util.concurrent.CompletableFuture;

/** A real block-built island; placement is spread across ticks. */
public final class IslandBuilder {
    public static final int FLOOR=100, HALF_MINE=7, MINE_BOTTOM=94;
    public static final class VoidGenerator extends ChunkGenerator {
        @Override public boolean shouldGenerateNoise(){return false;}
        @Override public boolean shouldGenerateSurface(){return false;}
        @Override public boolean shouldGenerateBedrock(){return false;}
        @Override public boolean shouldGenerateCaves(){return false;}
        @Override public boolean shouldGenerateDecorations(){return false;}
        @Override public boolean shouldGenerateMobs(){return false;}
        @Override public boolean shouldGenerateStructures(){return false;}
    }
    record Op(int x,int y,int z, Material m) {}
    private final JavaPlugin plugin;
    private final World world;
    private final Random random;
    private final int cx,cz;
    private final List<Op> ops=new ArrayList<>();
    IslandBuilder(JavaPlugin plugin, World world, int cx,int cz,int seed) {
        this.plugin=plugin;this.world=world;this.cx=cx;this.cz=cz;this.random=new Random(seed*734287L+9819L);
    }
    void put(int x,int y,int z,Material m){ops.add(new Op(cx+x,y,cz+z,m));}
    void box(int x1,int y1,int z1,int x2,int y2,int z2,Material m){
        for(int x=x1;x<=x2;x++) for(int y=y1;y<=y2;y++) for(int z=z1;z<=z2;z++) put(x,y,z,m);
    }
    void build(Consumer<Boolean> done){
        // Circular floating terrain, layered with grass and natural stone.
        for(int x=-33;x<=33;x++) for(int z=-33;z<=33;z++) {
            double d=Math.sqrt(x*x+z*z); if(d>32.3)continue;
            int bottom=FLOOR-3-(int)((32-d)*.55)-random.nextInt(3);
            for(int y=bottom;y<=FLOOR;y++) {
                Material m = y==FLOOR ? Material.GRASS_BLOCK : y>=FLOOR-2 ? Material.DIRT : random.nextInt(6)==0?Material.ANDESITE:Material.STONE;
                put(x,y,z,m);
            }
        }
        // Ring path and safe arrival path.
        for(int x=-28;x<=28;x++)for(int z=-28;z<=28;z++){
            double d=Math.sqrt(x*x+z*z);
            if((d>=15.5&&d<=18.5)||(Math.abs(x)<=2&&z>=14&&z<=27))
                put(x,FLOOR,z,random.nextInt(5)==0?Material.MOSSY_COBBLESTONE:Material.STONE_BRICKS);
        }
        // Quarry wall, rim and ore, resettable interior.
        for(int x=-9;x<=9;x++)for(int z=-9;z<=9;z++){
            if(Math.abs(x)>=8||Math.abs(z)>=8){
                for(int y=93;y<=100;y++)put(x,y,z,(Math.abs(x)==9||Math.abs(z)==9)?Material.STONE_BRICKS:Material.STONE);
                put(x,101,z,Material.SPRUCE_FENCE);
            }else for(int y=MINE_BOTTOM;y<=FLOOR;y++) put(x,y,z,ore(random,1));
        }
        // Small bridge across rim at the south face.
        for(int x=-1;x<=1;x++)for(int z=8;z<=13;z++)put(x,101,z,Material.SPRUCE_PLANKS);
        for(int x=-1;x<=1;x++)put(x,101,8,Material.AIR);
        // Entrance pad.
        box(-4,100,22,4,100,29,Material.SPRUCE_PLANKS);
        for(int x:new int[]{-4,4}) for(int z:new int[]{22,29}){
            box(x,101,z,x,104,z,Material.STRIPPED_SPRUCE_LOG);put(x,105,z,Material.LANTERN);
        }
        // Storage lodge and upgrade workshop.
        house(-25,-8,9,8); house(16,12,9,8);
        // Block-built drill over the mine: supports, arm, bit, glints.
        for(int x:new int[]{11,14}) for(int z:new int[]{-12,-9}){
            box(x,101,z,x,110,z,Material.DARK_OAK_LOG); put(x,111,z,Material.LANTERN);
        }
        box(10,110,-13,15,111,-8,Material.SPRUCE_PLANKS);
        box(3,110,-11,13,110,-10,Material.STRIPPED_SPRUCE_LOG);
        box(3,103,-10,4,109,-9,Material.COPPER_BLOCK);
        put(3,102,-10,Material.IRON_BLOCK);put(4,102,-9,Material.IRON_BLOCK);
        put(3,101,-10,Material.ANVIL);
        // Decorative machinery; functional actions open via menu.
        box(-23,101,-6,-22,101,-6,Material.BARREL);put(-21,101,-6,Material.CHEST);
        put(20,101,15,Material.SMITHING_TABLE);put(22,101,15,Material.BLAST_FURNACE);
        // Trees and flowers deliberately clear of functional areas.
        for(int[] p:new int[][]{{-24,17},{-27,7},{24,-19},{-12,-25},{9,-27},{27,2}}) tree(p[0],p[1]);
        for(int[] p:new int[][]{{-17,19},{-20,21},{-27,12},{21,-23},{7,-22},{26,7},{12,23}}){put(p[0],101,p[1],Material.FERN);put(p[0]+1,101,p[1],Material.POPPY);}
        for(int[] p:new int[][]{{-14,14},{14,14},{-14,-14},{14,-14},{-4,18},{4,18}}){
            put(p[0],101,p[1],Material.COBBLESTONE_WALL);put(p[0],102,p[1],Material.LANTERN);
        }
        // Load the whole footprint asynchronously before placing blocks. Hold chunks
        // while building so generation never waits on chunk IO in the placement loop.
        List<CompletableFuture<Chunk>> futures=new ArrayList<>();
        for(int x=(cx-34)>>4;x<=((cx+34)>>4);x++)for(int z=(cz-34)>>4;z<=((cz+34)>>4);z++)futures.add(world.getChunkAtAsync(x,z,true));
        CompletableFuture.allOf(futures.toArray(new CompletableFuture[0])).whenComplete((v,error)->{
            if(!plugin.isEnabled())return;
            Bukkit.getScheduler().runTask(plugin,()->{
                if(error!=null){plugin.getLogger().severe("Chunk preloading failed: "+error);done.accept(false);return;}
                List<Chunk> chunks=new ArrayList<>();
                for(var f:futures){Chunk chunk=f.join();chunk.addPluginChunkTicket(plugin);chunks.add(chunk);}
                new BukkitRunnable(){int i=0; public void run(){
                    try {
                        long deadline=System.nanoTime()+3_000_000L;
                        int end=Math.min(i+400,ops.size());
                        for(;i<end && System.nanoTime()<deadline;i++){Op o=ops.get(i);world.getBlockAt(o.x,o.y,o.z).setType(o.m,false);}
                        if(i>=ops.size()){cancel();chunks.forEach(c->c.removePluginChunkTicket(plugin));done.accept(true);}
                    }catch(Exception ex){cancel();chunks.forEach(c->c.removePluginChunkTicket(plugin));plugin.getLogger().severe("Island generation failed: "+ex);done.accept(false);}
                }}.runTaskTimer(plugin,1,1);
            });
        });
    }
    void house(int x,int z,int w,int d){
        box(x,100,z,x+w-1,100,z+d-1,Material.COBBLESTONE);
        for(int px=x;px<x+w;px++)for(int pz=z;pz<z+d;pz++){
            boolean edge=px==x||px==x+w-1||pz==z||pz==z+d-1;
            if(edge)for(int y=101;y<=105;y++)put(px,y,pz,(px==x||px==x+w-1)&&(pz==z||pz==z+d-1)?Material.SPRUCE_LOG:Material.SPRUCE_PLANKS);
        }
        // Door and windows are open apertures; all protected against break/place.
        for(int y=101;y<=102;y++)put(x+w/2,y,z+d-1,Material.AIR);
        put(x+2,103,z,Material.GLASS_PANE);put(x+w-3,103,z,Material.GLASS_PANE);
        for(int layer=0;layer<4;layer++){
            for(int px=x-1+layer;px<=x+w-layer;px++)for(int pz=z-1;pz<=z+d;pz++)put(px,106+layer,pz,Material.SPRUCE_PLANKS);
        }
        put(x+1,104,z+1,Material.LANTERN);
    }
    void tree(int x,int z){
        box(x,101,z,x,105,z,Material.SPRUCE_LOG);
        for(int y=103;y<=107;y++){int r=y>=106?1:2;for(int dx=-r;dx<=r;dx++)for(int dz=-r;dz<=r;dz++)if(Math.abs(dx)+Math.abs(dz)<=r+1)put(x+dx,y,z+dz,Material.SPRUCE_LEAVES);}
        put(x,108,z,Material.SPRUCE_LEAVES);
    }
    static Material ore(Random r,int level){int n=r.nextInt(100);if(n<3+level)return Material.DIAMOND_ORE;if(n<10+level*2)return Material.GOLD_ORE;if(n<30+level*3)return Material.IRON_ORE;if(n<58)return Material.COAL_ORE;return Material.STONE;}
    static boolean isMineBlock(Material m){return m==Material.STONE||m==Material.COAL_ORE||m==Material.IRON_ORE||m==Material.GOLD_ORE||m==Material.DIAMOND_ORE;}
}
