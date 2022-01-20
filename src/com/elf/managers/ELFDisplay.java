package com.elf.managers;

import org.lwjgl.LWJGLException;
import org.lwjgl.Sys;
import org.lwjgl.opengl.*;

public class ELFDisplay {

    private static int WIDTH = 1280;
    private static int HEIGHT = 720;
    private static int CAP = 120;

    private static String TITLE = "ELF";

    public static void create() throws LWJGLException {

        ContextAttribs attribs = new ContextAttribs(3, 2)
                .withForwardCompatible(true)
                .withProfileCore(true);

        Display.setDisplayMode(new DisplayMode(WIDTH, HEIGHT));
        Display.create(new PixelFormat(), attribs);

        GL11.glViewport(0, 0, WIDTH, HEIGHT);

    }

    public static void update() {
        Display.sync(CAP);
        Display.setTitle(TITLE);
        Display.update();
    }

    public static void destroy() {
        Display.destroy();
    }

    private static long getTime() {
        return System.currentTimeMillis();
    }

}
