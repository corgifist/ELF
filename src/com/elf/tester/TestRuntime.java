package com.elf.tester;

import com.elf.geometry.RawModel;
import com.elf.managers.ELFDisplay;
import com.elf.managers.ELFLoader;
import com.elf.render.ELFRenderer;
import org.lwjgl.LWJGLException;
import org.lwjgl.opengl.Display;

public class TestRuntime {
    public static void run() throws LWJGLException {
        ELFDisplay.create();

        ELFLoader loader = new ELFLoader();
        ELFRenderer renderer = new ELFRenderer();


        float[] vertices = {
                -0.5f, 0.5f, 0f,
                -0.5f, -0.5f, 0f,
                0.5f, -0.5f, 0f,
                0.5f, -0.5f, 0f,
                0.5f, 0.5f, 0f,
                -0.5f, 0.5f, 0f
        };

        RawModel model = loader.loadToVAO(vertices);

        while (!Display.isCloseRequested()) {
            renderer.prepare();
            renderer.render(model);
            ELFDisplay.update();
        }
    }
}
