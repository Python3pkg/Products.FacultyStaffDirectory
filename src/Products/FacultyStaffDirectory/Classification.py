# -*- coding: utf-8 -*-

__author__ = """WebLion <support@weblion.psu.edu>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.FacultyStaffDirectory.PersonGrouping import PersonGrouping
from Products.Relations.field import RelationField
from Products.FacultyStaffDirectory.config import *
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget
from Products.CMFCore.permissions import View, ManageProperties, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from zope.interface import implements
from Products.CMFCore.permissions import ManageUsers
from Products.membrane.interfaces import IPropertiesProvider
from Products.FacultyStaffDirectory.interfaces.classification import IClassification
from Acquisition import aq_inner, aq_parent
from Products.FacultyStaffDirectory.permissions import ASSIGN_CLASSIFICATIONS_TO_PEOPLE
from Products.FacultyStaffDirectory.interfaces import IGroupingProvidingMembership

schema = Schema((

    RelationField(
        name='people',
        widget=ReferenceBrowserWidget(
            label=u'People',
            label_msgid='FacultyStaffDirectory_label_people',
            i18n_domain='FacultyStaffDirectory',
            base_query={'portal_type':'FSDPerson', 'sort_on':'getSortableName'},
            allow_browse=0,
            allow_search=1,
            show_results_without_query=1,            
        ),
        write_permission=ASSIGN_CLASSIFICATIONS_TO_PEOPLE,
        allowed_types=('FSDPerson',),
        multiValued=1,
        relationship='classifications_people'
    ),
),
)

Classification_schema = getattr(PersonGrouping, 'schema', Schema(())).copy() + schema.copy()

class Classification(PersonGrouping):
    """
    """
    security = ClassSecurityInfo()
    meta_type = portal_type = "FSDClassification"
    # zope3 interfaces
    implements(IClassification, IPropertiesProvider, IGroupingProvidingMembership)
    _at_rename_after_creation = True
    schema = Classification_schema
    # Methods
    security.declareProtected(View, 'getPeople')
    def getPeople(self):
        """ Return a list of people in this classification, filtered by the current context
        """

        #There *has* to be a better way to do this...
        localPeople = self.getReferences()

        #Return the intersection of people referenced to this classification and people within/referenced to the parent
        return list(set(localPeople) & set(self.aq_parent.getPeople()))
    

    #
    # Validators
    #
    security.declarePrivate('validate_id')
    def validate_id(self, value):
        """Ensure the id is unique, also among groups globally
        """
        if value != self.getId():
            parent = aq_parent(aq_inner(self))
            if value in parent.objectIds():
                return "An object with id '%s' already exists in this folder" % value
        
            groups = getToolByName(self, 'portal_groups')
            if groups.getGroupById(value) is not None:
                return "A group with id '%s' already exists in the portal" % value

registerType(Classification, PROJECTNAME)
