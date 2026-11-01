package ru.prisonevo;
import org.junit.jupiter.api.Test;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;
class MathsTest {
 @Test void spiralAllocatesUniqueCells(){Set<String> cells=new HashSet<>();for(int n=0;n<100_000;n++){int[] c=Maths.cell(n);assertTrue(cells.add(c[0]+","+c[1]),"duplicate at "+n);}}
 @Test void storageStopsAtCapacity(){assertEquals(100,Maths.accrue(98,100,10000,5,9));assertEquals(5,Maths.accrue(5,100,4,5,9));assertEquals(23,Maths.accrue(5,100,10,5,9));}
 @Test void upgradesStayBounded(){assertEquals(5,Maths.cycleSeconds(99,30));assertEquals(500,Maths.upgradeCost(1));assertEquals(10000,Maths.capacity(10,1000));}
}
