package io.jans.ca.server;

import io.jans.ca.common.ErrorResponse;
import io.jans.ca.common.Jackson2;
import jakarta.ws.rs.WebApplicationException;
import org.apache.commons.io.IOUtils;
import org.apache.commons.lang.StringUtils;

import java.io.IOException;
import java.io.InputStream;
import java.util.List;

import static org.testng.AssertJUnit.assertTrue;

/**
 * @author Yuriy Zabrovarnyy
 * @version 0.9, 21/08/2013
 */

public class TestUtils {

    private TestUtils() {
    }

    public static void notEmpty(String str) {
        assertTrue(StringUtils.isNotBlank(str));
    }

    public static void notEmpty(List<String> str) {
        assertTrue(str != null && !str.isEmpty() && StringUtils.isNotBlank(str.get(0)));
    }

    public static ErrorResponse asError(WebApplicationException e) throws IOException {
        final Object entity = e.getResponse().getEntity();
        String entityAsString = null;
        if (entity instanceof String) {
            entityAsString = (String) entity;
        } else if (entity instanceof InputStream) {
            entityAsString = IOUtils.toString((InputStream) entity, "UTF-8");
        } else {
            throw new RuntimeException("Failed to identify type of the entity");
        }
        System.out.println(entityAsString);
        return Jackson2.createJsonMapper().readValue(entityAsString, ErrorResponse.class);
    }
}
