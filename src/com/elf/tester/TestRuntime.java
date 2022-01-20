package com.elf.tester;

import com.elf.managers.ELFDisplay;
import org.lwjgl.LWJGLException;
import org.lwjgl.opengl.Display;

public class TestRuntime {
    public static void run() throws LWJGLException {
        ELFDisplay.create();

        while (!Display.isCloseRequested()) {
            ELFDisplay.update();
        }
    }
}
