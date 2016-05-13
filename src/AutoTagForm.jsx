import React from 'react';
import ReactDOM from 'react-dom';
import Range from 'react-range';
import 'react-select/dist/react-select.css';
import './webtagging.css';

import Token from './Token';
import Image from './Image';
import Tag from './Tag';
import User from './User';
import {union, intersection, difference} from './SetUtils';

import AutoTagToolbar from './AutoTagToolbar';
import AutoTagTable from './AutoTagTable';
import TagSelectModal from './TagSelectModal';

export default class AutoTagForm extends React.Component {

  constructor() {
    super();

    this.state = {
      images: new Set(),
      users: new Map(),
      tags: new Map(),
      tokenMap: new Map(),
      unmappedTags: new Set(),
      showUnmapped: false,
      requiredTokenCardinality: 2,
      maxTokenCardinality: 2
    }

    // Abort capable AJAX variables
    this.loadRequest = undefined;

    // Prebind this to callback methods
    this.onSubmit = this.onSubmit.bind(this);
    this.cellCheckedChange = this.cellCheckedChange.bind(this);
    this.handleCheckedChangeAll = this.handleCheckedChangeAll.bind(this);
    this.selectMapping = this.selectMapping.bind(this);
    this.newMapping = this.newMapping.bind(this);
    this.addMapping = this.addMapping.bind(this);
    this.refreshForm = this.refreshForm.bind(this);
    this.toggleUnmapped = this.toggleUnmapped.bind(this);
    this.handleChangeRequiredTokenCardinality = this.handleChangeRequiredTokenCardinality.bind(this);

  }

  setEmptyState() {
    this.setState({
      images: new Set(),
      users: new Map(),
      tags: new Map(),
      tokenMap: new Map(),
      unmappedTags: new Set(),
      requiredTokenCardinality: 2,
      maxTokenCardinality: 2
    });
  }

  tokenValueCheck (tokenValue) {

    // Reject empty tokens
    if (tokenValue.length === 0) {
      return false;
    }

    // Reject tokens that are just numbers and/or symbols
    if ( /^([0-9-\;\.\(\)]+)$/.test(tokenValue) ) {
      return false;
    }

    // Accept any combination of letters, numbers and symbols
    if ( /^([\s\-_A-Za-z0-9-\;\.\(\)]+)$/.test(tokenValue) ) {
      return true;
    }

    // Reject anything else
    return false;

  }

  addOrUpdateToken(image, tagValuesMap, tokenMap, value) {

    let token;

    // TODO Do filtering here

    // If the token is already in the map, just update that entry
    if (tokenMap.has(value)) {
      token = tokenMap.get(value);
      token.increment();

    // Otherwise, create the entry and do any token -> tag matching
    } else {
      token = new Token(value);
      tokenMap.set(value, token);

      // When a token is first added, attempt to match it to tags
      if (tagValuesMap.has(value)) {
        let tags = tagValuesMap.get(value);

        // Set the possible list to all the tags found (at least 1)
        token.possible = new Set(tags);

        // If there is just the one possible mapping, mark it active
        if (tags.size === 1) {
          token.setActive(tags.values().next().value);
        }
      }

    }

    return token;

  }

  tokensInName(image, tagValuesMap, tokenMap) {

    let imageTokens = new Set();

    let tokens = image.clientPath.split(/[\/\\_\.\s]+/);
    tokens.forEach(value =>
      imageTokens.add(this.addOrUpdateToken(image, tagValuesMap, tokenMap, value))
    );

    // Return the set of tokens that are present on this image
    return imageTokens;

  }

  loadFromServer(imageIds) {

    // If there is a request in progress, abort it in favour of this one
    if (this.loadRequest && this.loadRequest.readyState !== 4) {
      this.loadRequest.abort();
    }

    // If there is nothing to display, just reset to default state
    if (imageIds.length === 0) {
      this.setEmptyState();
      // And bail
      return;
    }

    this.loadRequest = $.ajax({
      url: this.props.url,
      type: "POST",
      data: { imageIds: imageIds },
      dataType: 'json',
      cache: false
    });

    this.loadRequest.done(jsonData => {

        // All users map, id -> User
        let users = new Map();

        // All tags map, id -> Tag
        let tags = new Map();

        // Tag values map, value -> [ids]
        let tagValuesMap = new Map();

        // Process users
        jsonData.users.forEach(jsonUser => {
          let user = new User(
            jsonUser.id,
            jsonUser.omeName,
            jsonUser.firstName,
            jsonUser.lastName,
            jsonUser.email
          );
          users.set(user.id, user);
        });

        // Process tags
        jsonData.tags.forEach(jsonTag => {

          // Resolve the owner ID to a user
          let tagOwner = users.get(jsonTag.ownerId);

          // Add the mapping from id to Tag
          let tag = new Tag(
            jsonTag.id,
            jsonTag.value,
            jsonTag.description,
            tagOwner,
            jsonTag.permsCss,
            jsonTag.set
          );
          tags.set(tag.id, tag);

          // Create an entry if necessary and add this tag as a potential
          // match for the tag's value
          if (!tagValuesMap.has(tag.value)) {
            tagValuesMap.set(tag.value, new Set([tag]));
          } else {
            tagValuesMap.get(tag.value).add(tag);
          }

        });

        // Set of all tags which are used in at least one image, irrespective of
        // whether there is a token mapping using it or possible using it
        let allAppliedTags = new Set();

        // The possible mapping of tokens to tags
        // The active mapping
        // Counts of token use
        let tokenMap = new Map();

        let images = new Set();

        // Process the images
        jsonData.images.forEach(jsonImage => {

          // Resolve the owner ID to a user
          let imageOwner = users.get(jsonImage.ownerId);

          // Get the tags that correspond to these tagIds
          let imageTags = new Set(
            jsonImage.tags.map(
              jsonTagId => tags.get(jsonTagId)
            )
          );

          // Add the image to the set
          let image = new Image(
            jsonImage.id,
            jsonImage.name,
            imageOwner,
            jsonImage.permsCss,
            jsonImage.clientPath,
            imageTags
          );
          images.add(image);


          // Find the tokens on each image, updating the tokenMap in place
          image.tokens = this.tokensInName(image, tagValuesMap, tokenMap);

          // Check any tokens that exist on this image by default
          image.checkedTokens = new Set(image.tokens);

          // Add any tags found on this image to this definitive set of used
          // tags
          allAppliedTags = union(allAppliedTags, image.tags);

        });

        // Process the images again now that the token->tag map is complete as
        // the image may have tags applied for token->tag mappings where it
        // does not have the token. These should also be marked as checked
        // automatically

        // Get the reverse mapping of the tags to tokens. This is only possible
        // because there should be a 1:1 mapping between tokens and tags
        let activeTagTokenMap = new Map([...tokenMap].filter(
          kv => kv[1].isActive()
        ).map(
          kv => [kv[1].activeTag, kv[1]]
        ));

        // Also get the activeTagTokenMap as a Set for set operations
        let activeTagSet = new Set(activeTagTokenMap.keys());

        // Find the tags which are mapped in some way
        let mappedTags = new Set();
        tokenMap.forEach(token => {
          mappedTags = union(mappedTags, token.possible);
        });

        // Find the tags that are not applied in any way
        let unmappedTags = difference(allAppliedTags, mappedTags);


        // Check tokens due to applied tags for auto-mappings and
        // Check tags due to applied tags where there are no mappings
        images.forEach(image => {

          // Get the set of tags on this image that are currently mapped
          let appliedImageTags = intersection(activeTagSet, image.tags);

          // Lookup the tokens which those tags are mapped to and mark them
          // as checked
          appliedImageTags.forEach(tag => {
            let token = activeTagTokenMap.get(tag);
            image.checkToken(token);
          });

          // Get the set of tags that are on the image, but not involved in
          // any mapping. Apply this to checkedTags
          image.checkedTags = intersection(image.tags, unmappedTags);

        });

        // Set the state
        // Special case requiredTokenCardinality for when there is only one image
        this.setState({
          images: images,
          users: users,
          tags: tags,
          tokenMap: tokenMap,
          unmappedTags: unmappedTags,
          requiredTokenCardinality: images.size === 1 ? 1 : 2,
          maxTokenCardinality: images.size
        });

      }
    );

    //   error: function(xhr, status, err) {
    //     console.error(this.props.url, status, err.toString());
    //   }.bind(this)
    // });
  }

  componentDidMount() {
    this.loadFromServer(this.props.imageIds);
  }

  componentWillReceiveProps(nextProps) {
    // If the sizes are not the same we should definitely reload
    if (nextProps.imageIds.size !== this.props.imageIds.size) {
      this.loadFromServer(nextProps.imageIds);
      // Bail out as a reload was required and done
      return;
    }

    // If the sets are the same size, then compare the values.
    if (
      difference(new Set(nextProps.imageIds), new Set(this.props.imageIds)).size > 0 ||
      difference(new Set(this.props.imageIds), new Set(nextProps.imageIds)).size > 0
    ) {
      this.loadFromServer(nextProps.imageIds);
      // Bail out as a reload was required and done
      return;
    }

  }

  onSubmit(e) {
    e.preventDefault()

    // Get the active token -> tag mappings only
    let tokenMapActive = new Map([...this.state.tokenMap].filter(
      kv => kv[1].isActive()
    ));

    // Examine each image for changes
    let changes = [];
    let newImages = new Set();
    this.state.images.forEach(image => {
      let additions = [];
      let removals = [];

      // For each mapped token in the tokenTagMap compare its checked status
      // to the tagged status
      tokenMapActive.forEach(token => {
        let tag = token.activeTag;

        // Check if the user has permission to annotate this tag to this image
        if (tag.canAnnotate() && image.canAnnotate()) {

          // Get the checked and tagged states
          let checked = image.checkedTokens.has(token);
          let tagged = image.tags.has(tag);

          // Only add/remove if there has been a change
          // Assume success and thus update the image
          if (checked !== tagged) {
            // Addition
            if (checked) {
              additions.push(tag);
            // Removal
            } else {
              removals.push(tag);
            }
          }
        }

      });

      // For each of the unmapedTags compare its checked status to its tagged
      // status
      this.state.unmappedTags.forEach(tag => {

        // Get the checked and tagged states
        let checked = image.checkedTags.has(tag);
        let tagged = image.tags.has(tag);

        // Check if the user has permission to annotate this tag to this image
        if (tag.canAnnotate() && image.canAnnotate()) {

          // Only add/remove if there has been a change
          // Assume success and thus update the image
          if (checked !== tagged) {
            // Addition
            if (checked) {
              additions.push(tag);
            // Removal
            } else {
              removals.push(tag);
            }
          }
        }
      });

      // Add this image additions and removals to the payload
      if (additions.length > 0 || removals.length > 0) {
        changes.push({
          'imageId': image.id,
          'additions': additions.map(tag => tag.id),
          'removals': removals.map(tag => tag.id)
        });

        // If there were updates, then assume success, dirty the image and the
        // applied tags and add/remove the additions/removals
        let newImage = image.clone();
        newImage.tags = new Set(newImage.tags);
        newImage.tags = union(newImage.tags, additions);
        newImage.tags = difference(newImage.tags, new Set(removals));
        newImages.add(newImage);
      } else {
        newImages.add(image);
      }

    });

    // If there are no changes, no persistence is required
    if (changes.length === 0) {
      return;
    }

    this.setState({
      images: newImages
    });

    $.ajax({
      url: this.props.urlUpdate,
      type: "POST",
      data: JSON.stringify(changes),
      success: function(data) {
        // No action required
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());

        // TODO Pop up a warning dialog

        // Completely reload as the state could have been partially updated
        // or failed for complex reasons due to updates outside of the scope
        // of autotag
        this.refreshForm();

      }.bind(this)
    });

  }

  cellCheckedChange(image, tokenOrTag) {
    // Add/remove the token or tag depending on if it is current present

    // Dirty the image and checkedTokens/checkedTags
    let newImage = image.clone();

    if (tokenOrTag instanceof Token) {
      newImage.checkedTokens = new Set(image.checkedTokens);
      newImage.checkedTokens.has(tokenOrTag) ? newImage.checkedTokens.delete(tokenOrTag): newImage.checkedTokens.add(tokenOrTag);
    } else if (tokenOrTag instanceof Tag) {
      newImage.checkedTags = new Set(image.checkedTags);
      newImage.checkedTags.has(tokenOrTag) ? newImage.checkedTags.delete(tokenOrTag): newImage.checkedTags.add(tokenOrTag);
    }

    this.state.images.delete(image);
    this.state.images.add(newImage);

    // And update state
    this.setState({
      images: this.state.images
    });

  }

  handleCheckedChangeAll(tokenOrTag, selectAll) {
    // Add/remove the token or tag to all images depending on if it is current present

    // Create mix of dirty and original images
    let newImages;
    if (tokenOrTag instanceof Token) {
      newImages = new Set([...this.state.images].map(image => {

        // If the image is not already correctly checked
        if (selectAll !== image.checkedTokens.has(tokenOrTag)) {
          // Mark image and checkedTokens dirty
          let newImage = image.clone();
          newImage.checkedTokens = new Set(image.checkedTokens);
          selectAll ? newImage.checkedTokens.add(tokenOrTag): newImage.checkedTokens.delete(tokenOrTag);
          return newImage;
        }
        // Otherwise, return the existing image
        return image;
      }));

    } else if (tokenOrTag instanceof Tag) {

      newImages = new Set([...this.state.images].map(image => {

        // If the image is not already correctly checked
        if (selectAll !== image.checkedTags.has(tokenOrTag)) {
          // Mark image and checkedTags dirty
          let newImage = image.clone();
          newImage.checkedTags = new Set(image.checkedTags);
          selectAll ? newImage.checkedTags.add(tokenOrTag): newImage.checkedTags.delete(tokenOrTag);
          return newImage;
        }
        // Otherwise, return the existing image
        return image;
      }));
    }

    // Update state
    this.setState({
      images: newImages
    });
  }

  selectMapping(token, tag) {

    // TODO Check if this tag is already assigned to some other column?

    // Recalculate the checked state of this column for each image row
    for (let image of this.state.images) {
      // Determine if the image should be checked for this mapping either
      // because it has the token or it has the tag applied
      let checked = image.tokens.has(token) || image.tags.has(tag);

      // Update the image if necessary
      if (checked !== image.checkedTokens.has(token)) {
        checked ? image.checkedTokens.add(token) : image.checkedTokens.delete(token);
      }
    }

    // Update the tokenMap
    token.setActive(tag);

    // Update state.
    // Mark tokenMap dirty
    this.setState({
      images: this.state.images,
      tokenMap: new Map(this.state.tokenMap)
    });

  }

  newMapping(token) {

    let $dialog = $('<div>').dialog({

      title: 'Choose Tag',
      resizable: false,
      height: 320,
      width:420,
      modal: true,


      close: function(e){
        ReactDOM.unmountComponentAtNode(this);
        $( this ).remove();
      }
    });

    let closeDialog = function(e){
      e.preventDefault();
      $dialog.dialog('close');
    }

    ReactDOM.render(
      <TagSelectModal closeDialog={closeDialog}
                      token={token}
                      tags={this.state.tags}
                      tokenMap={this.state.tokenMap}
                      addMapping={this.addMapping}
      />,
      $dialog[0]
    );
  }

  addMapping(token, tag, tagValue, tagDescription) {
    // Undefined tagValue means this is an existing tag
    if (tagValue === undefined && tag !== undefined){
      // Add the tag to the tokenMap for this token
      token.possible.add(tag);

      // Remove the tag from the unmapped Tags
      this.state.unmappedTags.delete(tag);

      this.setState({
        tokenMap: this.state.tokenMap,
        unmappedTags: this.state.unmappedTags
      });

      this.selectMapping(token, tag);

    // This is a new tag
    } else if (tagValue !== undefined){
      // Create the tag. In this case we can not update the form until the
      // ajax call is successful as the tag ID is not known until it returns
      // and that is important imformation
      $.ajax({
        url: this.props.urlCreateTag,
        type: "POST",
        data: JSON.stringify({
          value: tagValue,
          description: tagDescription
        }),
        dataType: 'json',
        success: function(jsonTag) {

          // Resolve the owner ID to a user
          let tagOwner = this.state.users.get(jsonTag.ownerId);

          // Add the mapping from id to Tag
          let tag = new Tag(
            jsonTag.id,
            jsonTag.value,
            jsonTag.description,
            tagOwner,
            jsonTag.permsCss,
            jsonTag.set
          );
          this.state.tags.set(tag.id, tag);

          // Add the tag to the tokenMap for this token
          token.possible.add(tag);

          this.setState({
            tokenMap: this.state.tokenMap,
            unmappedTags: this.state.unmappedTags,
            tags: this.state.tags
          });

          this.selectMapping(token, tag);

        }.bind(this),
        error: function(xhr, status, err) {
          console.error(this.props.url, status, err.toString());
        }.bind(this)
      });
    }
  }

  refreshForm() {
    this.loadFromServer(this.props.imageIds);
  }

  toggleUnmapped() {
    this.setState({
      showUnmapped: !this.state.showUnmapped
    });
  }

  handleChangeRequiredTokenCardinality(value) {
    this.setState({
      requiredTokenCardinality: value
    });
  }

  filteredTokenMap() {
    // Filter out any tokens that do not meet the requirements
    // Requirements for inclusion:
    // 1) Matches an existing tag value
    // 2) Is present on required number of images AND Is not numbers and/or symbols only
    let tokenMap = new Map([...this.state.tokenMap].filter(kv => {
      let token = kv[1];

      return (
        token.possible.size > 0 ||
        (
          token.count >= this.state.requiredTokenCardinality &&
          this.tokenValueCheck(token.value)
        )
      )

    }));
    return tokenMap;
  }

  render() {
    return (
      <form ref="form" onSubmit={this.onSubmit} id="updateAllForm" className={'autotagForm'}>

        <AutoTagToolbar requiredTokenCardinality={this.state.requiredTokenCardinality}
                        maxTokenCardinality={this.state.maxTokenCardinality}
                        showUnmapped={this.state.showUnmapped}
                        handleChangeRequiredTokenCardinality={this.handleChangeRequiredTokenCardinality}
                        toggleUnmapped={this.toggleUnmapped}
                        refreshForm={this.refreshForm}
        />

        <AutoTagTable tokenMap={this.filteredTokenMap()}
                      images={this.state.images}
                      unmappedTags={this.state.unmappedTags}
                      showUnmapped={this.state.showUnmapped}
                      requiredTokenCardinality={this.state.requiredTokenCardinality}
                      cellCheckedChange={this.cellCheckedChange}
                      selectMapping={this.selectMapping}
                      newMapping={this.newMapping}
                      handleCheckedChangeAll={this.handleCheckedChangeAll}

        />
      </form>
    );
  }
}
