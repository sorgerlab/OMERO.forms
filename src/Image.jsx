class Image {
  constructor(id, name, owner, permissions, clientPath, tags, tokens=new Set(), checkedTokens=new Set(), checkedTags=new Set()) {
    this.id = id
    this.name = name;
    this.owner = owner;
    this.permissions = permissions;
    this.clientPath = clientPath;
    this.tags = tags;
    this.tokens = tokens;
    this.checkedTokens = checkedTokens;
    this.checkedTags = checkedTags;

    // Speed up this lookup
    this._canAnnotate = this.permissions.indexOf("canAnnotate") != -1
  }

  checkToken(token) {
    this.checkedTokens.add(token);
  }

  uncheckToken(token) {
    this.checkedToken.delete(token);
  }

  canAnnotate() {
    return this._canAnnotate;
  }

  clone() {
    return new Image(
      this.id,
      this.name,
      this.owner,
      this.permissions,
      this.clientPath,
      this.tags,
      this.tokens,
      this.checkedTokens,
      this.checkedTags
    );
  }

}

export default Image;
