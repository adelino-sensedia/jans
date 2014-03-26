package org.gluu.site.ldap.exception;

/**
 * Duplicate LDAP entry exception
 * 
 * @author Pankaj
 */
public class DuplicateEntryException extends LugeException {
	/**
	 * Serialization ID
	 */
	private static final long serialVersionUID = 6749290172742578916L;

	/**
	 * Default constructor
	 */
	public DuplicateEntryException() {
		super("Entry already exists");
	}

	/**
	 * Constructor for returning the offending DN
	 * 
	 * @param dn
	 *            DN that returned a duplicate
	 */
	public DuplicateEntryException(final String dn) {
		super("Entry already exists: " + dn);
	}
}
