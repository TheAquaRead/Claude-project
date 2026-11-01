package ru.prisonevo;

public final class Maths {
    private Maths() {}
    // Integer spiral: no duplicate cell and stable forever.
    public static int[] cell(int n) {
        if (n < 0) throw new IllegalArgumentException("negative index");
        if (n == 0) return new int[]{0,0};
        int ring=(int)Math.ceil((Math.sqrt(n+1.0)-1.0)/2.0);
        int side=2*ring; int max=(2*ring+1)*(2*ring+1)-1; int d=max-n;
        if(d<side) return new int[]{ring-d,-ring};
        if(d<2*side) return new int[]{-ring,-ring+(d-side)};
        if(d<3*side) return new int[]{-ring+(d-2*side),ring};
        return new int[]{ring,ring-(d-3*side)};
    }
    public static long capacity(int level,int base) { return Math.multiplyExact((long)base, level); }
    public static long upgradeCost(int level){return 500L*level*level;}
    public static int cycleSeconds(int level,int base){return Math.max(5,base-(level-1)*2);}
    public static long output(int level,int base){return (long)base*level;}
    public static long accrue(long stored,long capacity,long elapsedSeconds,int seconds,long perCycle) {
        if(stored>=capacity || elapsedSeconds<seconds) return stored;
        long cycles=elapsedSeconds/seconds; long room=capacity-stored;
        return stored+Math.min(room,cycles>room/perCycle ? room : cycles*perCycle);
    }
}
