package ru.prisonevo;

/** Pure slot mapping, matching the six-row chest textures. */
final class UiLayout {
    enum Page { MAIN, STORAGE, DRILL, MINE, UPGRADES, HELP }
    static String action(Page page,int slot) {
        if(slot<0||slot>=54)return "none";
        int row=slot/9,col=slot%9;
        if(row==5) {
            if(col<3)return page==Page.MAIN?"leave":"back";
            return col==8?"close":"info";
        }
        if(page==Page.MAIN) {
            if(row<3)return col<3?"home":col<6?"drill":"storage";
            return col<3?"mine":col<6?"upgrades":"help";
        }
        if(page==Page.HELP)return "info";
        if(page==Page.UPGRADES) {
            if(row<3)return col<4?"speed":"power";
            return col<4?"capacity":"quality";
        }
        if(col<4)return "info";
        return switch(page) {
            case STORAGE -> row<3?"sell":"capacity";
            case DRILL -> row<3?"speed":"power";
            case MINE -> row<3?"quality":"help";
            default -> "none";
        };
    }
    static String compact(long value) {
        if(value<10000)return Long.toString(value);
        if(value<1_000_000)return Math.round(value/1000.0)+"k";
        return String.format(java.util.Locale.ROOT,"%.1fM",value/1_000_000.0);
    }
}
