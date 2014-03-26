package org.gluu.site.ldap.persistence.exception;

/**
 * An exception is a result of something screwy in the O-R mappings.
 */
public class MappingException extends LdapMappingException {

	private static final long serialVersionUID = 1113352885909511209L;

	public MappingException(String msg, Throwable root) {
		super(msg, root);
	}

	public MappingException(Throwable root) {
		super(root);
	}

	public MappingException(String s) {
		super(s);
	}

}
