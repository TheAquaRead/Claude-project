package ru.prisonevo;

import java.util.UUID;

public class IslandData {
    public final UUID owner;
    public final int index;
    public boolean built;
    public int speed = 1;
    public int power = 1;
    public int storage = 1;
    public int mine = 1;
    public long balance;
    public long stored;
    public long lastTick;
    public long resetAt;
    public String returnWorld;
    public double returnX, returnY, returnZ;
    public float returnYaw, returnPitch;
    public IslandData(UUID owner, int index) { this.owner=owner; this.index=index; }
}
