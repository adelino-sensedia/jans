/*
 * oxd-server
 * oxd-server
 *
 * OpenAPI spec version: 4.2
 * Contact: yuriyz@gluu.org
 *
 * NOTE: This class is auto generated by the swagger code generator program.
 * https://github.com/swagger-api/swagger-codegen.git
 * Do not edit the class manually.
 */

package io.swagger.client.model;

import java.util.Objects;
import java.util.Arrays;
import com.google.gson.TypeAdapter;
import com.google.gson.annotations.JsonAdapter;
import com.google.gson.annotations.SerializedName;
import com.google.gson.stream.JsonReader;
import com.google.gson.stream.JsonWriter;
import io.swagger.v3.oas.annotations.media.Schema;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
/**
 * GetAccessTokenByRefreshTokenParams
 */


public class GetAccessTokenByRefreshTokenParams {
  @SerializedName("oxd_id")
  private String oxdId = null;

  @SerializedName("refresh_token")
  private String refreshToken = null;

  @SerializedName("scope")
  private List<String> scope = new ArrayList<String>();

  public GetAccessTokenByRefreshTokenParams oxdId(String oxdId) {
    this.oxdId = oxdId;
    return this;
  }

   /**
   * Get oxdId
   * @return oxdId
  **/
  @Schema(example = "bcad760f-91ba-46e1-a020-05e4281d91b6", required = true, description = "")
  public String getOxdId() {
    return oxdId;
  }

  public void setOxdId(String oxdId) {
    this.oxdId = oxdId;
  }

  public GetAccessTokenByRefreshTokenParams refreshToken(String refreshToken) {
    this.refreshToken = refreshToken;
    return this;
  }

   /**
   * Get refreshToken
   * @return refreshToken
  **/
  @Schema(example = "33d7988e-6ffb-4fe5-8c2a-0e158691d446", required = true, description = "")
  public String getRefreshToken() {
    return refreshToken;
  }

  public void setRefreshToken(String refreshToken) {
    this.refreshToken = refreshToken;
  }

  public GetAccessTokenByRefreshTokenParams scope(List<String> scope) {
    this.scope = scope;
    return this;
  }

  public GetAccessTokenByRefreshTokenParams addScopeItem(String scopeItem) {
    this.scope.add(scopeItem);
    return this;
  }

   /**
   * Get scope
   * @return scope
  **/
  @Schema(example = "[\"openid\"]", required = true, description = "")
  public List<String> getScope() {
    return scope;
  }

  public void setScope(List<String> scope) {
    this.scope = scope;
  }


  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    GetAccessTokenByRefreshTokenParams getAccessTokenByRefreshTokenParams = (GetAccessTokenByRefreshTokenParams) o;
    return Objects.equals(this.oxdId, getAccessTokenByRefreshTokenParams.oxdId) &&
        Objects.equals(this.refreshToken, getAccessTokenByRefreshTokenParams.refreshToken) &&
        Objects.equals(this.scope, getAccessTokenByRefreshTokenParams.scope);
  }

  @Override
  public int hashCode() {
    return Objects.hash(oxdId, refreshToken, scope);
  }


  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class GetAccessTokenByRefreshTokenParams {\n");
    
    sb.append("    oxdId: ").append(toIndentedString(oxdId)).append("\n");
    sb.append("    refreshToken: ").append(toIndentedString(refreshToken)).append("\n");
    sb.append("    scope: ").append(toIndentedString(scope)).append("\n");
    sb.append("}");
    return sb.toString();
  }

  /**
   * Convert the given object to string with each line indented by 4 spaces
   * (except the first line).
   */
  private String toIndentedString(Object o) {
    if (o == null) {
      return "null";
    }
    return o.toString().replace("\n", "\n    ");
  }

}
