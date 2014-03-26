package org.gluu.site.ldap.persistence.annotation;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * LDAP Json Object
 * 
 * @author Yuriy Movchan Date: 01/31/2014
 */
@Target({ ElementType.FIELD })
@Retention(RetentionPolicy.RUNTIME)
public @interface LdapJsonObject {
}