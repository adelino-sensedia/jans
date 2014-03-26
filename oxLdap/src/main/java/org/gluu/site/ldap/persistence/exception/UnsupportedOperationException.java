package org.gluu.site.ldap.persistence.exception;

/**
 * An exception is a result if LDAP server doesn't support operation.
 * 
 * @author Yuriy Movchan Date: 08.07.2012
 */
public class UnsupportedOperationException extends LdapMappingException {

	private static final long serialVersionUID = 2321766232087075304L;

	public UnsupportedOperationException(Throwable root) {
		super(root);
	}

	public UnsupportedOperationException(String string, Throwable root) {
		super(string, root);
	}

	public UnsupportedOperationException(String s) {
		super(s);
	}

}
