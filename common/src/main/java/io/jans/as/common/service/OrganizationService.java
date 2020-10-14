/*
 * Janssen Project software is available under the MIT License (2008). See http://opensource.org/licenses/MIT for full text.
 *
 * Copyright (c) 2020, Janssen Project
 */

package io.jans.as.common.service;

import io.jans.as.persistence.model.GluuOrganization;
import io.jans.as.model.configuration.AppConfiguration;
import io.jans.orm.PersistenceEntryManager;
import io.jans.service.BaseCacheService;
import io.jans.service.CacheService;
import io.jans.service.LocalCacheService;
import io.jans.util.OxConstants;

import javax.enterprise.context.ApplicationScoped;
import javax.inject.Inject;
import javax.inject.Named;

@ApplicationScoped
@Named("organizationService")
public class OrganizationService extends io.jans.service.OrganizationService {

    private static final long serialVersionUID = -8966940469789981584L;
    public static final int ONE_MINUTE_IN_SECONDS = 60;

    @Inject
	private AppConfiguration appConfiguration;

	@Inject
	private PersistenceEntryManager ldapEntryManager;

	@Inject
	private CacheService cacheService;

    @Inject
    private LocalCacheService localCacheService;

	/**
	 * Update organization entry
	 * 
	 * @param organization
	 *            Organization
	 */
	public void updateOrganization(GluuOrganization organization) {
		ldapEntryManager.merge(organization);
	}

	public GluuOrganization getOrganization() {
    	BaseCacheService usedCacheService = getCacheService();
        return usedCacheService.getWithPut(OxConstants.CACHE_ORGANIZATION_KEY, () -> ldapEntryManager.find(GluuOrganization.class, getDnForOrganization()), ONE_MINUTE_IN_SECONDS);
	}

	public String getDnForOrganization() {
		return "o=gluu";
	}

    private BaseCacheService getCacheService() {
    	if (appConfiguration.getUseLocalCache()) {
    		return localCacheService;
    	}
    	
    	return cacheService;
    }

}
