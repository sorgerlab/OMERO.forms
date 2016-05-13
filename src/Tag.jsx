export default class Tag {
  constructor(id, value, description, owner, permissions, set) {
    this.id = id
    this.value = value;
    this.description = description;
    this.owner = owner;
    this.permissions = permissions;
    this.set = set;

    // Speed up this lookup
    this._canAnnotate = this.permissions.indexOf("canAnnotate") != -1
  }

  canAnnotate() {
    return this._canAnnotate;
  }

}
