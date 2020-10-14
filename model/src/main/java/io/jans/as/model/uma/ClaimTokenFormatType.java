/*
 * Janssen Project software is available under the MIT License (2008). See http://opensource.org/licenses/MIT for full text.
 *
 * Copyright (c) 2020, Janssen Project
 */

package io.jans.as.model.uma;

/**
 * @author yuriyz on 05/30/2017.
 */
public enum ClaimTokenFormatType {
    ID_TOKEN("http://openid.net/specs/openid-connect-core-1_0.html#IDToken");

    private String value;

    ClaimTokenFormatType(String value) {
        if (value == null || value.trim().isEmpty()) {
            throw new IllegalArgumentException();
        }
        this.value = value;
    }

    public String getValue() {
        return value;
    }

    public static ClaimTokenFormatType fromValue(String value) {
        for (ClaimTokenFormatType type : values()) {
            if (type.getValue().equals(value)) {
                return type;
            }
        }
        return null;
    }

    public static boolean isValueValid(String value) {
        return fromValue(value) != null;
    }
}
