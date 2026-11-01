package ru.prisonevo;

import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.Player;
import org.bukkit.event.*;
import org.bukkit.event.inventory.*;
import org.bukkit.inventory.*;
import org.bukkit.inventory.meta.ItemMeta;
import net.kyori.adventure.key.Key;
import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.format.NamedTextColor;
import net.kyori.adventure.text.format.TextDecoration;

final class ModernMenu implements Listener {
    private final PrisonEvo plugin;
    private static final Key GUI=Key.key("prisonevo:gui"), SPACING=Key.key("prisonevo:spacing");
    static final class Holder implements InventoryHolder {
        final UUID owner; final UiLayout.Page page; Inventory inventory;
        Holder(UUID owner,UiLayout.Page page){this.owner=owner;this.page=page;}
        @Override public Inventory getInventory(){return Objects.requireNonNull(inventory);}
    }
    ModernMenu(PrisonEvo plugin){this.plugin=plugin;}
    private int base(String key,int fallback){return plugin.getConfig().getInt(key,fallback);}
    private static Component shift(int n) {
        if(n< -512||n>512)throw new IllegalArgumentException("UI offset: "+n);
        return Component.text(String.valueOf((char)(0xE400+n+512))).font(SPACING);
    }
    private static int width(String s) {
        int n=0;for(char c:s.toCharArray())n+=c==' '?4:c=='.'?2:c=='k'?5:6;
        // Bitmap font advances include the trailing pixel.
        return n;
    }
    private static Component data(String value,int x,int y) {
        return shift(x).append(Component.text(value).font(Key.key("prisonevo:data_"+y)).color(NamedTextColor.DARK_GRAY))
            .append(shift(-x-width(value)));
    }
    private Component title(UiLayout.Page page,IslandData d) {
        Component title=shift(-8).append(Component.text(String.valueOf((char)(0xE001+page.ordinal()))).font(GUI).color(NamedTextColor.WHITE)).append(shift(-177));
        long cap=d==null?0:Maths.capacity(d.storage,base("starting-capacity",1000));
        if(page==UiLayout.Page.MAIN)title=title.append(data(d==null?"0/0":UiLayout.compact(d.stored)+"/"+UiLayout.compact(cap),82,113));
        if(d!=null)switch(page) {
            case STORAGE -> title=title.append(data(UiLayout.compact(d.stored)+"/"+UiLayout.compact(cap),12,96));
            case DRILL -> title=title.append(data(d.speed+" / 10",86,49)).append(data(d.power+" / 10",86,90)).append(data(Long.toString(Maths.output(d.power,base("base-cycle-output",2))),30,96));
            case MINE -> {
                long secs=Math.max(0,(d.resetAt-System.currentTimeMillis()+999)/1000);
                title=title.append(data(d.mine+" / 10",99,49)).append(data(String.format(Locale.ROOT,"%02d:%02d",secs/60,secs%60),27,96));
            }
            default -> {}
        }
        return title.decoration(TextDecoration.ITALIC,false);
    }
    void open(Player p,UiLayout.Page page) {
        IslandData d=plugin.uiData(p); if(d!=null)plugin.update(d);
        if(d==null&&page!=UiLayout.Page.MAIN&&page!=UiLayout.Page.HELP) {
            plugin.message(p,"§eСначала создай остров: нажми «Остров».");return;
        }
        Holder h=new Holder(p.getUniqueId(),page);h.inventory=Bukkit.createInventory(h,54,title(page,d));
        for(int slot=0;slot<54;slot++)h.inventory.setItem(slot,button(UiLayout.action(page,slot),d,page));
        p.openInventory(h.inventory);
    }
    private ItemStack button(String action,IslandData d,UiLayout.Page page) {
        String name="§7Информация";List<String> lore=new ArrayList<>();
        switch(action) {
            case "home" -> {name=d==null?"§aСоздать остров":"§aМой остров";lore.add("§7Перейти на свой шахтёрский остров");}
            case "drill" -> {name="§6Бур";lore.add("§7Параметры и улучшения автодобычи");}
            case "storage" -> {name="§bХранилище";lore.add("§7Общая добыча и продажа");}
            case "mine" -> {name="§bШахта";lore.add("§7Качество руды и время обновления");}
            case "upgrades" -> {name="§eРазвитие острова";lore.add("§7Бур, хранилище и шахта");}
            case "help" -> {name="§eКак играть";lore.add("§7Короткая инструкция по добыче");}
            case "leave" -> {name="§7На сервер";lore.add("§7Вернуться в сохранённую точку входа");}
            case "back" -> name="§7В главное меню";
            case "close" -> name="§cЗакрыть";
            case "sell" -> {name="§aПродать всю добычу";lore.add("§7Продажа за внутренние монеты PrisonEvo");lore.add("§7Курс этой версии: §f1 добыча = 1 монета");}
            case "speed", "power", "capacity", "quality" -> {
                int lvl=d==null?1:switch(action){case "speed"->d.speed;case "power"->d.power;case "capacity"->d.storage;default->d.mine;};
                name="§e"+switch(action){case "speed"->"Скорость бура";case "power"->"Мощность бура";case "capacity"->"Вместимость склада";default->"Качество шахты";};
                lore.add("§7Уровень: §f"+lvl+" / 10");
                if(lvl>=10)lore.add("§aМаксимальный уровень");
                else {lore.add("§7Цена: §e"+Maths.upgradeCost(lvl)+" монет PrisonEvo");lore.add("§eНажми для покупки улучшения");}
            }
            default -> {
                name="§7PrisonEvo";
                if(page==UiLayout.Page.HELP)lore.add("§7Вся добыча хранится общим счётчиком.");
            }
        }
        if(d!=null) {
            lore.add(" ");lore.add("§7Склад: §f"+d.stored+" / "+Maths.capacity(d.storage,base("starting-capacity",1000)));
            lore.add("§7Баланс: §e"+d.balance+" монет PrisonEvo");
            if(action.equals("drill")||page==UiLayout.Page.DRILL) {
                lore.add("§7За цикл: §f"+Maths.output(d.power,base("base-cycle-output",2)));
                lore.add("§7Время цикла: §f"+Maths.cycleSeconds(d.speed,base("base-cycle-seconds",30))+" сек.");
                lore.add(d.stored>=Maths.capacity(d.storage,base("starting-capacity",1000))?"§eСклад заполнен":"§aБур работает");
            }
            if(action.equals("mine")||page==UiLayout.Page.MINE)lore.add("§7До обновления: §f"+Math.max(0,(d.resetAt-System.currentTimeMillis())/1000)+" сек.");
        }
        ItemStack item=plugin.item(Material.PAPER,name,lore.toArray(String[]::new));
        ItemMeta meta=item.getItemMeta();meta.setItemModel(new NamespacedKey("prisonevo","ui_button"));item.setItemMeta(meta);return item;
    }
    @EventHandler(priority=EventPriority.HIGHEST) public void click(InventoryClickEvent e) {
        if(!(e.getView().getTopInventory().getHolder() instanceof Holder h))return;
        e.setCancelled(true);
        if(!(e.getWhoClicked() instanceof Player p)||!h.owner.equals(p.getUniqueId()))return;
        String action=UiLayout.action(h.page,e.getRawSlot());
        if(action.equals("none")||action.equals("info"))return;
        // Bukkit requires inventory opening/closing to run outside the click callback.
        Bukkit.getScheduler().runTask(plugin,()-> {
            if(p.isOnline()&&p.getOpenInventory().getTopInventory().getHolder()==h)handle(p,h,action);
        });
    }
    private void handle(Player p,Holder h,String action) {
        if(!p.hasPermission("prisonevo.use")){p.closeInventory();return;}
        switch(action) {
            case "close" -> {p.closeInventory();return;}
            case "back" -> {open(p,UiLayout.Page.MAIN);return;}
            case "home" -> {p.closeInventory();plugin.enter(p);return;}
            case "leave" -> {p.closeInventory();plugin.leave(p);return;}
            case "help" -> {open(p,UiLayout.Page.HELP);return;}
            case "drill" -> {open(p,UiLayout.Page.DRILL);return;}
            case "storage" -> {open(p,UiLayout.Page.STORAGE);return;}
            case "mine" -> {open(p,UiLayout.Page.MINE);return;}
            case "upgrades" -> {open(p,UiLayout.Page.UPGRADES);return;}
        }
        IslandData d=plugin.uiData(p);if(d==null||!plugin.uiWritable())return;
        plugin.update(d);
        if(action.equals("sell")) {
            if(d.stored==0)plugin.message(p,"Хранилище пусто.");
            else {
                long sold=d.stored;
                try {long next=Math.addExact(d.balance,sold);d.balance=next;d.stored=0;if(plugin.persist())plugin.message(p,"§aПродано: §f"+sold+" §7| Баланс: §e"+d.balance);}
                catch(ArithmeticException overflow){plugin.message(p,"§cБаланс достиг предела. Продажа отменена.");}
            }
        } else {
            String type=switch(action){case "speed"->"speed";case "power"->"power";case "capacity"->"storage";case "quality"->"mine";default->null;};
            if(type!=null)plugin.upgradeValue(p,d,type);
        }
        open(p,h.page);
    }
    @EventHandler(priority=EventPriority.HIGHEST) public void drag(InventoryDragEvent e) {
        if(e.getView().getTopInventory().getHolder() instanceof Holder)e.setCancelled(true);
    }
}
