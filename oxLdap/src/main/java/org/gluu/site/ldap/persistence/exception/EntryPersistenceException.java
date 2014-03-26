package org.gluu.site.ldap.persistence.exception;

/**
 * An exception is a result if LDAP entry defined incorrectly.
 * 
 * @author Yuriy Movchan Date: 10.07.2010
 */
public class EntryPersistenceException extends LdapMappingException {

	private static final long serialVersionUID = 1321766232087075304L;

	public EntryPersistenceException(Throwable root) {
		super(root);
	}

	public EntryPersistenceException(String string, Throwable root) {
		super(string, root);
	}

	public EntryPersistenceException(String s) {
		super(s);
	}

}
