package ru.prisonevo;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
class UiLayoutTest {
    @Test void entireCardsShareTheirAction() {
        for(int row=0;row<3;row++)for(int col=0;col<9;col++)
            assertEquals(col<3?"home":col<6?"drill":"storage",UiLayout.action(UiLayout.Page.MAIN,row*9+col));
        for(int row=0;row<5;row++)for(int col=4;col<9;col++)
            assertEquals(row<3?"sell":"capacity",UiLayout.action(UiLayout.Page.STORAGE,row*9+col));
    }
    @Test void lowerInventoryAndOutsideClicksNeverTriggerActions() {
        for(UiLayout.Page page:UiLayout.Page.values())for(int slot:new int[]{-999,-1,54,55,80,89})assertEquals("none",UiLayout.action(page,slot));
    }
    @Test void allPagesHaveBackOrExitAndClose() {
        for(UiLayout.Page page:UiLayout.Page.values()) {
            assertEquals(page==UiLayout.Page.MAIN?"leave":"back",UiLayout.action(page,45));
            assertEquals("close",UiLayout.action(page,53));
        }
    }
    @Test void largeCapacitiesFitStatusSpace() {
        assertEquals("640",UiLayout.compact(640));assertEquals("10k",UiLayout.compact(10000));
        assertEquals("10.0M",UiLayout.compact(10000000));
        assertTrue((UiLayout.compact(9999999)+"/"+UiLayout.compact(10000000)).length()<=13);
        for(long capacity:new long[]{1000,10000,99999,999999,1000000,10000000})
            assertTrue((UiLayout.compact(capacity)+"/"+UiLayout.compact(capacity)).length()<=11);
    }
}
