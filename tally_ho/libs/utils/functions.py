from tally_ho.apps.tally.models.center import Center
from tally_ho.apps.tally.models.station import Station
from tally_ho.apps.tally.models.candidate import Candidate


def disableEnableEntity(centerCode, stationNumber, disableReason=None):
    entities = []
    entity_to_return = None
    status_target = False
    try:
        if stationNumber:
            entity_to_return = Station.objects.get(station_number=stationNumber,
                                                   center__code=centerCode)
            status_target = not entity_to_return.active

            entities.append(entity_to_return)
        else:
            entity_to_return = Center.objects.get(code=centerCode)
            status_target = not entity_to_return.active

            entities.append(entity_to_return)
            entities += Station.objects.filter(center__code=centerCode)
    except Center.DoesNotExist:
        raise forms.ValidationError(_(u"Center Number does not exist"))
    except Station.DoesNotExist:
        raise forms.ValidationError(_(u"Station Number does not exist"))
    else:
        for oneEntity in entities:
            oneEntity.active = status_target

            oneEntity.disable_reason = 0
            if disableReason is not None:
                oneEntity.disable_reason = disableReason

            oneEntity.save()
        return entity_to_return


def disableEnableCandidate(candidateId):
    entity_to_return = None
    status_target = False

    try:
        entity_to_return = Candidate.objects.get(candidate_id=candidateId)
        status_target = not entity_to_return.active

    except Candidate.DoesNotExist:
        raise forms.ValidationError(_(u"Candidate does not exist"))
    else:
        entity_to_return.active = status_target
        entity_to_return.save()

        return entity_to_return
