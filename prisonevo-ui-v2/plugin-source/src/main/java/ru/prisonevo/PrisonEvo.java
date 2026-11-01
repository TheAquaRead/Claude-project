package ru.prisonevo;

import org.bukkit.*;
import org.bukkit.block.Block;
import org.bukkit.command.*;
import org.bukkit.entity.*;
import org.bukkit.event.*;
import org.bukkit.event.block.*;
import org.bukkit.event.entity.*;
import org.bukkit.event.inventory.*;
import org.bukkit.event.player.*;
import org.bukkit.event.vehicle.VehicleMoveEvent;
import org.bukkit.generator.ChunkGenerator;
import org.bukkit.inventory.*;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.scheduler.BukkitRunnable;
import org.jetbrains.annotations.NotNull;
import java.io.*;
import java.util.*;
import java.util.logging.Level;
import net.kyori.adventure.text.Component;

public final class PrisonEvo extends JavaPlugin implements Listener, CommandExecutor {
    private World world; private IslandStore store; private int grid,radius,capacity,baseSeconds,baseOutput,offlineSeconds,resetSeconds;
    private final Set<UUID> building=new HashSet<>();
    private boolean writable=true;
    private ModernMenu modernMenu;
    IslandData uiData(Player p){return store.players.get(p.getUniqueId());}
    boolean uiWritable(){return writable;}
    private static final String PREFIX="§8[§dPrison§5Evo§8] §7";
    private static class MenuHolder implements InventoryHolder {
        final UUID owner; MenuHolder(UUID owner){this.owner=owner;} @Override public @NotNull Inventory getInventory(){throw new UnsupportedOperationException();}
    }
    @Override public ChunkGenerator getDefaultWorldGenerator(@NotNull String worldName,String id){return new IslandBuilder.VoidGenerator();}
    @Override public void onEnable(){
        saveDefaultConfig();String name=getConfig().getString("world","prison_evo");
        grid=getConfig().getInt("grid-size",2048);radius=getConfig().getInt("island-radius",48);
        capacity=getConfig().getInt("starting-capacity",1000);baseSeconds=getConfig().getInt("base-cycle-seconds",30);baseOutput=getConfig().getInt("base-cycle-output",2);
        offlineSeconds=Math.clamp(getConfig().getInt("offline-limit-hours",8),0,168)*3600;resetSeconds=getConfig().getInt("mine-reset-seconds",300);
        if(name==null||!name.matches("[A-Za-z0-9_-]+")||grid<256||grid>10000||radius<40||radius*2+32>=grid||capacity<1||capacity>1000000||baseSeconds<5||baseOutput<1||resetSeconds<30){
            getLogger().severe("Unsafe configuration; plugin disabled");getServer().getPluginManager().disablePlugin(this);return;
        }
        File dir=new File(Bukkit.getWorldContainer(),name);File marker=new File(dir,".prisonevo-world");
        World existing=Bukkit.getWorld(name); boolean previousWorld=marker.isFile();
        if((existing!=null||dir.exists())&&!marker.isFile()){
            getLogger().severe("Refusing to use existing unmarked world: "+name+". Choose a new world name.");getServer().getPluginManager().disablePlugin(this);return;
        }
        try{
            if(!dir.exists()&&!dir.mkdirs())throw new IOException("Cannot create world directory");
            if(!marker.exists()&&!marker.createNewFile())throw new IOException("Cannot create world marker");
            world=new WorldCreator(name).generator(new IslandBuilder.VoidGenerator()).environment(World.Environment.NORMAL).createWorld();
            if(world==null)throw new IOException("World could not be loaded");
            world.setSpawnLocation(0,120,0);world.setGameRule(GameRule.DO_MOB_SPAWNING,false);world.setGameRule(GameRule.DO_FIRE_TICK,false);
            world.setGameRule(GameRule.DO_DAYLIGHT_CYCLE,false);world.setTime(6000);world.setStorm(false);world.setPVP(false);
            store=new IslandStore(getDataFolder(),grid,name);
            if(previousWorld&&!new File(getDataFolder(),"islands.yml").isFile())throw new IOException("Existing world without islands.yml: restore matching data backup");
            store.load(); if(!previousWorld)store.save();
        }catch(Exception e){getLogger().log(Level.SEVERE,"Startup failed; refusing to run with missing or corrupt state",e);getServer().getPluginManager().disablePlugin(this);return;}
        getServer().getPluginManager().registerEvents(this,this);
        modernMenu=new ModernMenu(this);getServer().getPluginManager().registerEvents(modernMenu,this);
        Objects.requireNonNull(getCommand("prisonevo")).setExecutor(this);
        new BukkitRunnable(){long t=0;public void run(){
            t++;for(Player p:world.getPlayers()){
                IslandData d=store.players.get(p.getUniqueId());if(d==null||!d.built){eject(p);continue;}
                if(!allowed(p,p.getLocation())){p.teleport(home(d));continue;}
                update(d); if(d.resetAt<=System.currentTimeMillis())resetMine(d);
                if(t%2==0)animate(d,p);
            }
            if(t%15==0)persist();
        }}.runTaskTimer(this,40,40);
        getLogger().info("PrisonEvo enabled: personal island world "+name);
    }
    @Override public void onDisable(){if(store!=null)persist();}
    boolean persist(){try{store.save();return true;}catch(Exception ex){writable=false;getLogger().log(Level.SEVERE,"Data save failed. Changes are locked to prevent loss.",ex);return false;}}
    int[] center(IslandData d){int[] c=Maths.cell(d.index);return new int[]{c[0]*grid,c[1]*grid};}
    Location home(IslandData d){int[] c=center(d);return new Location(world,c[0]+.5,102,c[1]+25.5,180,0);}
    boolean allowed(Player p,Location loc){
        if(loc.getWorld()!=world)return true; IslandData d=store.players.get(p.getUniqueId());if(d==null||!d.built)return false;
        int[] c=center(d);double x=loc.getX()-c[0],z=loc.getZ()-c[1];return Math.abs(x)<=radius&&Math.abs(z)<=radius&&loc.getY()>=65&&loc.getY()<=180;
    }
    void message(CommandSender p,String text){p.sendMessage(PREFIX+text);}
    @Override public boolean onCommand(@NotNull CommandSender sender,@NotNull Command cmd,@NotNull String label,@NotNull String[] args){
        if(!(sender instanceof Player p)){sender.sendMessage("Use this command in-game.");return true;}
        if(!p.hasPermission("prisonevo.use")){message(p,"§cНет доступа.");return true;}
        String action=args.length==0?"menu":args[0].toLowerCase(Locale.ROOT);
        switch(action){case "menu" -> open(p);case "home" -> enter(p);case "leave" -> leave(p);default -> message(p,"Команды: §f/pe menu §7| §f/pe home §7| §f/pe leave");}return true;
    }
    void enter(Player p){
        if(!writable){message(p,"§cДанные временно недоступны. Сообщите администрации.");return;}
        if(building.contains(p.getUniqueId())){message(p,"Остров уже строится, подождите.");return;}
        IslandData d=store.players.get(p.getUniqueId());
        if(d==null){if(store.nextIndex>=100000){message(p,"§cНет свободных участков.");return;}
            d=new IslandData(p.getUniqueId(),store.nextIndex++);d.balance=Math.max(0,getConfig().getLong("starting-balance",0));d.lastTick=System.currentTimeMillis();store.players.put(d.owner,d);
            if(!persist()){message(p,"§cНе удалось сохранить участок.");return;}
        }
        if(p.getWorld()!=world){Location l=p.getLocation();d.returnWorld=l.getWorld().getName();d.returnX=l.getX();d.returnY=l.getY();d.returnZ=l.getZ();d.returnYaw=l.getYaw();d.returnPitch=l.getPitch();if(!persist()){message(p,"§cОшибка сохранения.");return;}}
        if(d.built){update(d);p.teleport(home(d));p.playSound(p.getLocation(),Sound.BLOCK_AMETHYST_BLOCK_CHIME,1,1);message(p,"Добро пожаловать на свой остров!");return;}
        building.add(d.owner);message(p,"§eСоздаём твой остров. Это займёт немного времени...");
        IslandData current=d;int[] c=center(d);
        new IslandBuilder(this,world,c[0],c[1],d.index).build(ok->{
            building.remove(current.owner);
            if(!ok){message(p,"§cНе удалось построить остров. Обратитесь к администрации.");return;}
            current.built=true;current.lastTick=System.currentTimeMillis();current.resetAt=System.currentTimeMillis()+resetSeconds*1000L;
            if(!persist()){current.built=false;message(p,"§cОстров построен, но не сохранён; сообщите администрации.");return;}
            if(p.isOnline()){p.teleport(home(current));p.playSound(p.getLocation(),Sound.UI_TOAST_CHALLENGE_COMPLETE,1,1);message(p,"§aТвой остров готов! §7Открой меню: §f/pe");}
        });
    }
    void leave(Player p){
        if(p.getWorld()!=world){message(p,"Ты не на острове.");return;}
        IslandData d=store.players.get(p.getUniqueId()); if(d!=null)update(d);
        Location target=returnLocation(d);if(target==null){message(p,"§cМир возврата недоступен. Обратитесь к администрации.");return;}
        if(p.teleport(target)){persist();message(p,"Ты вернулся на сервер.");}
    }
    Location returnLocation(IslandData d){
        if(d!=null&&d.returnWorld!=null){World w=Bukkit.getWorld(d.returnWorld);if(w!=null&&w!=world)return new Location(w,d.returnX,d.returnY,d.returnZ,d.returnYaw,d.returnPitch);}
        for(World w:Bukkit.getWorlds())if(w!=world)return w.getSpawnLocation();return null;
    }
    void eject(Player p){Location l=returnLocation(store.players.get(p.getUniqueId()));if(l!=null)p.teleport(l);}
    void update(IslandData d){
        long now=System.currentTimeMillis();long elapsed=Math.max(0,(now-d.lastTick)/1000L);int cycle=Maths.cycleSeconds(d.speed,baseSeconds);
        if(elapsed>=cycle){long allowed=Math.min(elapsed,offlineSeconds);d.stored=Maths.accrue(d.stored,Maths.capacity(d.storage,capacity),allowed,cycle,Maths.output(d.power,baseOutput));
            // Discard excess offline time; otherwise retain incomplete cycle.
            d.lastTick=elapsed>offlineSeconds?now:now-(elapsed%cycle)*1000L;}
    }
    void resetMine(IslandData d){
        int[] c=center(d);Random r=new Random(d.owner.getLeastSignificantBits()^System.currentTimeMillis());
        for(Player p:world.getPlayers())if(p.getUniqueId().equals(d.owner)&&inMine(d,p.getLocation()))p.teleport(home(d));
        for(int x=-7;x<=7;x++)for(int z=-7;z<=7;z++)for(int y=IslandBuilder.MINE_BOTTOM;y<=IslandBuilder.FLOOR;y++)world.getBlockAt(c[0]+x,y,c[1]+z).setType(IslandBuilder.ore(r,d.mine),false);
        d.resetAt=System.currentTimeMillis()+resetSeconds*1000L;
    }
    boolean inMine(IslandData d,Location l){if(l.getWorld()!=world)return false;int[] c=center(d);return Math.abs(l.getBlockX()-c[0])<=7&&Math.abs(l.getBlockZ()-c[1])<=7&&l.getBlockY()>=IslandBuilder.MINE_BOTTOM&&l.getBlockY()<=IslandBuilder.FLOOR;}
    void animate(IslandData d,Player p){
        int[] c=center(d);double phase=(System.currentTimeMillis()%2400L)*Math.PI*2/2400.0;
        Location shaft=new Location(world,c[0]+3.5,103.2,c[1]-9.5);
        for(int i=0;i<6;i++){double angle=phase+i*Math.PI/3;Location spark=shaft.clone().add(Math.cos(angle)*.65,i*.22,Math.sin(angle)*.65);world.spawnParticle(Particle.ELECTRIC_SPARK,spark,1,0,0,0,0);}
        world.spawnParticle(Particle.SMOKE,shaft.clone().add(0,6,0),2,.15,.1,.15,.005);
    }
    ItemStack item(Material m,String name,String... lore){ItemStack i=new ItemStack(m);ItemMeta meta=i.getItemMeta();meta.setDisplayName(name);meta.setLore(Arrays.asList(lore));i.setItemMeta(meta);return i;}
    void open(Player p){
        if(getConfig().getBoolean("ui.enabled",false)){modernMenu.open(p,UiLayout.Page.MAIN);return;}
        IslandData d=store.players.get(p.getUniqueId());if(d!=null)update(d);
        Inventory inv=Bukkit.createInventory(new MenuHolder(p.getUniqueId()),54,"§8§lPRISON§5§lEVO");
        ItemStack frame=item(Material.GRAY_STAINED_GLASS_PANE," ");for(int k=0;k<54;k++)inv.setItem(k,frame);
        inv.setItem(10,item(Material.GRASS_BLOCK,"§a§lМОЙ ОСТРОВ","§7Твоя личная добывающая база","§e➜ Нажми, чтобы попасть на остров"));
        if(d==null){inv.setItem(13,item(Material.PANDA_SPAWN_EGG,"§d§lДОБРО ПОЖАЛОВАТЬ","§7Создай остров, чтобы начать!"));}
        else{
            long cap=Maths.capacity(d.storage,capacity);
            inv.setItem(12,item(Material.HOPPER,"§6§lБУР","§7Скорость: §f"+d.speed+" §8/ §f10","§7Добыча: §f"+d.power+" §8/ §f10","§7Каждые §f"+Maths.cycleSeconds(d.speed,baseSeconds)+" сек. §7добывает §f"+Maths.output(d.power,baseOutput),"§7Работает даже когда ты не в сети","§8Автономность ограничена настройкой сервера"));
            inv.setItem(13,item(Material.CHEST,"§b§lХРАНИЛИЩЕ","§7Заполнено: §f"+d.stored+" §8/ §f"+cap,"§7Монет PrisonEvo: §e"+d.balance,"§e➜ Нажми, чтобы продать всё"));
            inv.setItem(14,item(Material.NETHERITE_PICKAXE,"§d§lШАХТА","§7Уровень: §f"+d.mine+" §8/ §f10","§7Добывай блоки в карьере","§7и улучшай качество руды."));
            inv.setItem(28,upgrade(Material.CLOCK,"§6Скорость бура",d.speed));
            inv.setItem(30,upgrade(Material.PISTON,"§6Мощность бура",d.power));
            inv.setItem(32,upgrade(Material.BARREL,"§bВместимость склада",d.storage));
            inv.setItem(34,upgrade(Material.DIAMOND_ORE,"§dКачество шахты",d.mine));
        }
        inv.setItem(49,item(Material.OAK_DOOR,"§c§lВЕРНУТЬСЯ","§7Вернуться на анархию"));
        p.openInventory(inv);
    }
    ItemStack upgrade(Material m,String title,int lvl){return item(m,"§l"+title,"§7Уровень: §f"+lvl+" §8/ §f10",lvl>=10?"§aМаксимальный уровень":"§7Цена: §e"+Maths.upgradeCost(lvl)+" монет PrisonEvo","§e➜ Нажми для улучшения");}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true) public void click(InventoryClickEvent e){
        if(!(e.getView().getTopInventory().getHolder() instanceof MenuHolder h))return;
        e.setCancelled(true);if(!(e.getWhoClicked() instanceof Player p)||!h.owner.equals(p.getUniqueId()))return;
        int slot=e.getRawSlot();if(slot>=e.getView().getTopInventory().getSize()||slot<0)return;
        if(slot==10){p.closeInventory();enter(p);return;}if(slot==49){p.closeInventory();leave(p);return;}
        IslandData d=store.players.get(p.getUniqueId());if(d==null||!writable)return;update(d);
        if(slot==13){if(d.stored==0){message(p,"Хранилище пусто.");return;}long sold=d.stored;d.stored=0;d.balance=Math.addExact(d.balance,sold);if(persist())message(p,"§aПродано: §f"+sold+" §7| Баланс: §e"+d.balance);}
        if(slot==28)upgradeValue(p,d,"speed");if(slot==30)upgradeValue(p,d,"power");if(slot==32)upgradeValue(p,d,"storage");if(slot==34)upgradeValue(p,d,"mine");open(p);
    }
    void upgradeValue(Player p,IslandData d,String type){
        int lvl=switch(type){case "speed"->d.speed;case "power"->d.power;case "storage"->d.storage;default->d.mine;};
        if(lvl>=10){message(p,"§aДостигнут максимум.");return;}long cost=Maths.upgradeCost(lvl);if(d.balance<cost){message(p,"§cНе хватает монет PrisonEvo: нужно §e"+cost);return;}
        d.balance-=cost;switch(type){case "speed"->d.speed++;case "power"->d.power++;case "storage"->d.storage++;default->d.mine++;}
        if(persist()){p.playSound(p.getLocation(),Sound.ENTITY_PLAYER_LEVELUP,1,1.2f);message(p,"§aУлучшение приобретено!");}
    }
    @EventHandler public void drag(InventoryDragEvent e){if(e.getView().getTopInventory().getHolder() instanceof MenuHolder)e.setCancelled(true);}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true) public void teleport(PlayerTeleportEvent e){if(e.getTo()!=null&&e.getTo().getWorld()==world&&!allowed(e.getPlayer(),e.getTo())){e.setCancelled(true);message(e.getPlayer(),"§cЭтот участок тебе недоступен.");}}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true) public void move(PlayerMoveEvent e){
        if(e instanceof PlayerTeleportEvent||e.getTo()==null||e.getFrom().getWorld()!=world)return;
        if(e.getTo().getWorld()!=world||!allowed(e.getPlayer(),e.getTo())){
            if(e.getTo().getY()<65){IslandData d=store.players.get(e.getPlayer().getUniqueId());if(d!=null&&d.built){e.setTo(home(d));return;}}
            e.setTo(e.getFrom());
        }
    }
    @EventHandler public void join(PlayerJoinEvent e){if(e.getPlayer().getWorld()==world)getServer().getScheduler().runTask(this,()->{Player p=e.getPlayer();IslandData d=store.players.get(p.getUniqueId());if(d!=null&&d.built)p.teleport(home(d));else eject(p);});}
    @EventHandler(priority=EventPriority.HIGHEST) public void respawn(PlayerRespawnEvent e){
        Location dest=e.getRespawnLocation();if(dest.getWorld()==world&&!allowed(e.getPlayer(),dest)){
            IslandData d=store.players.get(e.getPlayer().getUniqueId());Location safe=d!=null&&d.built?home(d):returnLocation(d);if(safe!=null)e.setRespawnLocation(safe);
        }
    }
    @EventHandler public void changedWorld(PlayerChangedWorldEvent e){
        Player p=e.getPlayer();if(p.getWorld()==world&&!allowed(p,p.getLocation()))getServer().getScheduler().runTask(this,()->{if(p.isOnline()&&p.getWorld()==world&&!allowed(p,p.getLocation()))eject(p);});
    }
    @EventHandler public void quit(PlayerQuitEvent e){IslandData d=store.players.get(e.getPlayer().getUniqueId());if(d!=null){update(d);persist();}}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true) public void breaking(BlockBreakEvent e){
        Player p=e.getPlayer();if(p.getWorld()!=world)return;e.setCancelled(true);IslandData d=store.players.get(p.getUniqueId());
        if(d==null||!d.built||!allowed(p,p.getLocation())||!inMine(d,e.getBlock().getLocation())||!writable)return;
        Material type=e.getBlock().getType();if(!IslandBuilder.isMineBlock(type))return;
        if(d.stored>=Maths.capacity(d.storage,capacity)){message(p,"§cСклад заполнен. Продай добычу или улучши хранилище.");return;}
        long amount=switch(type){case DIAMOND_ORE->8;case GOLD_ORE->5;case IRON_ORE->3;case COAL_ORE->2;default->1;};
        d.stored=Math.min(Maths.capacity(d.storage,capacity),d.stored+amount);e.getBlock().setType(Material.AIR,false);
        p.spawnParticle(Particle.BLOCK,e.getBlock().getLocation().add(.5,.5,.5),8,.2,.2,.2,type.createBlockData());
        p.sendActionBar(Component.text("§bСклад: §f"+d.stored+" / "+Maths.capacity(d.storage,capacity)));
    }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true) public void place(BlockPlaceEvent e){if(e.getBlock().getWorld()==world)e.setCancelled(true);}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true) public void interact(PlayerInteractEvent e){
        if(e.getPlayer().getWorld()!=world)return;
        if(e.getAction()==Action.RIGHT_CLICK_BLOCK||e.getAction()==Action.PHYSICAL)e.setCancelled(true);
        if(e.getItem()!=null&&(e.getItem().getType()==Material.ENDER_PEARL||e.getItem().getType()==Material.CHORUS_FRUIT||e.getItem().getType()==Material.FIREWORK_ROCKET))e.setCancelled(true);
    }
    @EventHandler public void drop(PlayerDropItemEvent e){if(e.getPlayer().getWorld()==world)e.setCancelled(true);}
    @EventHandler public void bucketEmpty(PlayerBucketEmptyEvent e){if(e.getPlayer().getWorld()==world)e.setCancelled(true);}
    @EventHandler public void bucketFill(PlayerBucketFillEvent e){if(e.getPlayer().getWorld()==world)e.setCancelled(true);}
    @EventHandler public void portal(PlayerPortalEvent e){if(e.getFrom().getWorld()==world||(e.getTo()!=null&&e.getTo().getWorld()==world))e.setCancelled(true);}
    @EventHandler public void armor(PlayerArmorStandManipulateEvent e){if(e.getPlayer().getWorld()==world)e.setCancelled(true);}
    @EventHandler public void entityInteract(PlayerInteractEntityEvent e){if(e.getPlayer().getWorld()==world)e.setCancelled(true);}
    @EventHandler public void breakByEntity(EntityChangeBlockEvent e){if(e.getBlock().getWorld()==world)e.setCancelled(true);}
    @EventHandler public void explode(EntityExplodeEvent e){if(e.getLocation().getWorld()==world)e.blockList().clear();}
    @EventHandler public void explodeBlock(BlockExplodeEvent e){if(e.getBlock().getWorld()==world)e.blockList().clear();}
    @EventHandler public void burn(BlockBurnEvent e){if(e.getBlock().getWorld()==world)e.setCancelled(true);}
    @EventHandler public void spread(BlockSpreadEvent e){if(e.getBlock().getWorld()==world)e.setCancelled(true);}
    @EventHandler public void flow(BlockFromToEvent e){if(e.getBlock().getWorld()==world)e.setCancelled(true);}
    @EventHandler public void pistonExtend(BlockPistonExtendEvent e){if(e.getBlock().getWorld()==world)e.setCancelled(true);}
    @EventHandler public void pistonRetract(BlockPistonRetractEvent e){if(e.getBlock().getWorld()==world)e.setCancelled(true);}
    @EventHandler public void damage(EntityDamageEvent e){if(e.getEntity() instanceof Player && e.getEntity().getWorld()==world)e.setCancelled(true);}
}
